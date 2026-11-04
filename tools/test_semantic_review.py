"""Témoins négatifs pour éviter qu’un audit sémantique passe sans détecter les défauts."""
import unittest
from run_semantic_review import inspect


class SemanticAuditTests(unittest.TestCase):
    def page(self,content):
        return '<html lang="fr"><body><a href="#main-content">Aller au contenu</a><main id="main-content"><h1>Recette</h1>'+content+'</main></body></html>'

    def test_explicit_implicit_and_aria_names(self):
        html=self.page('<label for="name">Nom</label><input id="name"><label>Valider<input type="checkbox"></label><button aria-label="Fermer"><svg aria-hidden="true"></svg></button>')
        self.assertEqual(inspect(html),[])

    def test_unlabelled_control_is_reported(self):
        self.assertTrue(any('sans nom HTML' in issue for issue in inspect(self.page('<input id="unlabelled">'))))

    def test_broken_aria_reference_is_reported(self):
        self.assertTrue(any('cible absente missing' in issue for issue in inspect(self.page('<button aria-describedby="missing">Continuer</button>'))))

    def test_duplicate_id_is_reported(self):
        self.assertIn('Identifiant dupliqué : duplicate',inspect(self.page('<p id="duplicate">A</p><p id="duplicate">B</p>')))


if __name__=='__main__':unittest.main()
