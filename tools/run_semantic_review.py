#!/usr/bin/env python3
"""Repères, noms HTML et références ARIA : audit de rendu serveur, sans navigateur."""
from html.parser import HTMLParser
import json
from pathlib import Path
import secrets
import tempfile
from run_ux_review import prepare


class Tree(HTMLParser):
    VOID={'input','img','meta','link','br','hr','area','base','col','embed','param','source','track','wbr'}
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.nodes=[];self.stack=[];self.feed(html)
    def handle_starttag(self,tag,attrs):
        node={'tag':tag,'attrs':dict(attrs),'text':'','parents':self.stack.copy()}
        self.nodes.append(node)
        if tag not in self.VOID:self.stack.append(node)
    def handle_endtag(self,tag):
        for i in range(len(self.stack)-1,-1,-1):
            if self.stack[i]['tag']==tag:self.stack=self.stack[:i];break
    def handle_data(self,text):
        for node in self.stack:node['text']+=text


def inspect(html):
    nodes=Tree(html).nodes;issues=[];ids={}
    for n in nodes:
        key=n['attrs'].get('id')
        if key:
            if key in ids:issues.append('Identifiant dupliqué : '+key)
            ids[key]=n
    for n in nodes:
        a=n['attrs']
        for attr in ['aria-labelledby','aria-describedby','aria-controls']:
            for key in (a.get(attr) or '').split():
                if key not in ids:issues.append(f'{n["tag"]} {a.get("id",a.get("name",""))} : {attr} cible absente {key}')
        if n['tag']=='img' and 'alt' not in a:issues.append('Image sans attribut alt')
        if n['tag'] not in ['input','select','textarea','button']:continue
        if a.get('type')=='hidden':continue
        name=(a.get('aria-label') or '').strip()
        if not name and a.get('aria-labelledby'):
            name=' '.join(ids[key]['text'] for key in a['aria-labelledby'].split() if key in ids).strip()
        if not name:
            name=' '.join(p['text'] for p in n['parents'] if p['tag']=='label').strip()
        if not name and a.get('id'):
            name=' '.join(p['text'] for p in nodes if p['tag']=='label' and p['attrs'].get('for')==a['id']).strip()
        if not name and n['tag']=='button':name=n['text'].strip()
        if not name and n['tag']=='input' and a.get('type') in ['submit','button','reset']:name=(a.get('value') or '').strip()
        if not name:issues.append(f'Contrôle sans nom HTML identifié : {n["tag"]} {a.get("id",a.get("name",""))}')
    for tag in ['main','h1']:
        if sum(n['tag']==tag for n in nodes)!=1:issues.append('Un seul '+tag+' attendu')
    if not any(n['tag']=='html' and n['attrs'].get('lang')=='fr' for n in nodes):issues.append('Langue fr absente')
    if not any(n['tag']=='a' and n['attrs'].get('href')=='#main-content' for n in nodes) or 'main-content' not in ids:issues.append('Lien d’évitement/cible absent')
    return list(dict.fromkeys(issues))


def main():
    output=Path(tempfile.mkdtemp(prefix='pharmagest-semantic-report-'))
    report={'scope':'rendu HTML, pas arbre d’accessibilité ni lecteur d’écran','rows':[],'status':'en cours'}
    try:
        with tempfile.TemporaryDirectory(prefix='pharmagest-semantic-data-') as directory:
            cases=prepare(Path(directory),secrets.token_urlsafe(32))
            from django.test import Client
            from django.contrib.auth.models import User
            from pharmacy.models import Medicine,Sale,StockMovement
            def check(c,role,route,post=False):
                r=c.post(route,{}) if post else c.get(route)
                issues=inspect(r.content.decode()) if r.status_code==200 else ['HTTP '+str(r.status_code)]
                row={'role':role,'route':route,'method':'POST vide' if post else 'GET','result':'KO' if issues else 'OK HTML','issues':issues}
                report['rows'].append(row)
            for case in cases:
                c=Client();c.force_login(User.objects.get(username=case['username']))
                routes=case['routes']+([f'/ventes/{case["sale_id"]}/'] if case['sale_id'] else [])
                if case['wizard']:routes.append('/catalogue/medicaments/ajouter/')
                for route in routes:check(c,case['role'],route)
                if case['role']=='administrateur':
                    before=(Medicine.objects.count(),Sale.objects.count(),StockMovement.objects.count())
                    for route in routes:
                        if route.endswith(('/ajouter/','/reception/','/inventaire/')):check(c,case['role'],route,True)
                    assert before==(Medicine.objects.count(),Sale.objects.count(),StockMovement.objects.count()),'Mutation inattendue dans formulaire vide'
            c=Client()
            for route in ['/comptes/login/','/comptes/password_reset/']:check(c,'anonyme',route)
        report['status']='KO' if any(r['issues'] for r in report['rows']) else 'OK HTML, lecteur d’écran non exécuté'
    except Exception as exc:report.update(status='interrompu',error=str(exc))
    finally:
        (output/'summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        print('Résultats : '+str(output))
    for r in report['rows']:
        if r['issues']:print(r['role'],r['route'],r['method'],r['issues'])
    return 0 if report['status'].startswith('OK HTML') else 1


if __name__=='__main__':raise SystemExit(main())
