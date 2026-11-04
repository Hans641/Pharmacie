#!/usr/bin/env python3
"""Résume quinze durées humaines transmises, sans ouvrir de base ni de navigateur."""
import argparse
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import statistics
import tempfile


def durations(value):
    try:
        numbers=[float(part.strip().replace(',', '.')) for part in value.split(';')]
    except ValueError as exc:
        raise argparse.ArgumentTypeError('Saisir cinq durées en secondes séparées par ; (ex. 25,4;26;24;27;25).') from exc
    if len(numbers)!=5 or any(not math.isfinite(n) or n<=0 for n in numbers):
        raise argparse.ArgumentTypeError('Cinq durées strictement positives et finies sont requises par scénario.')
    return numbers


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--simple',type=durations,required=True)
    parser.add_argument('--trois-produits',type=durations,required=True)
    parser.add_argument('--ordonnance',type=durations,required=True)
    parser.add_argument('--conditions',required=True,help='Machine/navigateur/largeur/thème/connexion ; aucune donnée personnelle ni secret.')
    args=parser.parse_args()
    rows={}
    for scenario,values in [('simple',args.simple),('trois-produits',args.trois_produits),('ordonnance',args.ordonnance)]:
        rows[scenario]={'durations_seconds':values,'median_seconds':statistics.median(values),'minimum_seconds':min(values),'maximum_seconds':max(values)}
    report={'source':'durées déclarées par utilisateur ; mesure humaine non observée par le script','utc':datetime.now(timezone.utc).isoformat(),'conditions':args.conditions,'scope':'recherche à confirmation HTML et lien reçu ; PDF/connexion/ouverture brouillon exclus','scenarios':rows,'simple_median_under_30_seconds':rows['simple']['median_seconds']<30}
    output=Path(tempfile.mkdtemp(prefix='pharmagest-human-timing-report-'))
    (output/'summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    for name,row in rows.items():
        print(f'{name} : médiane {row["median_seconds"]:.2f} s ; min {row["minimum_seconds"]:.2f} s ; max {row["maximum_seconds"]:.2f} s')
    print('Médiane simple < 30 s : '+('oui, selon durées déclarées' if report['simple_median_under_30_seconds'] else 'non'))
    print('Résultats : '+str(output))


if __name__=='__main__':main()
