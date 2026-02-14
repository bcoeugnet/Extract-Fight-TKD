# Extract Fight TKD - CLUB ATHLETIQUE

Système de suivi des combats de Taekwondo pour le CLUB ATHLETIQUE lors de la Coupe IDF Benjamins Minimes.

## 🎯 Fonctionnalités

- **Extraction automatique** des combattants du CLUB ATHLETIQUE depuis le PDF
- **Site web GitHub Pages** affichant tous les combats et leurs statuts
- **Mise à jour automatique** du site via CI/CD GitHub Actions
- **Suivi en temps réel** des victoires et défaites

## 📊 Données Extraites

Le système extrait automatiquement :
- **11 combattants** du CLUB ATHLETIQUE
- Leurs **numéros de combattant**
- Leurs **couleurs** (Bleu/Rouge)
- Tous leurs **combats** (actuels et potentiels futurs)

### Nos Combattants

1. **Hawa DANSOUKHO** - #159 (Rouge)
2. **CHERINE FAKKOUL** - #151 (Rouge)
3. **RITEDJ SALEMKOUR** - #147 (Rouge)
4. **DOUNIA HENDA** - #146 (Bleu)
5. **Orso OLIVIERI** - #93 (Bleu)
6. **Alya ZENASNI** - #396 (Bleu)
7. **SELMA HENDA** - #150 (Bleu)
8. **Ismaïl SEBAA** - #152 (Bleu)
9. **MOHAMED MECHACHA** - #148 (Bleu)
10. **Iliyan-Yahya BARRY** - #245 (Bleu)
11. **RAYAN MEDROUH** - #149 (Bleu)

## 🚀 Utilisation

### Voir le site web

Une fois GitHub Pages activé, le site sera accessible à :
```
https://bcoeugnet.github.io/Extract-Fight-TKD/
```

### Mettre à jour les résultats des combats

1. Éditez le fichier `fight_results.json`
2. Ajoutez les résultats des combats terminés :

```json
{
  "fight_results": {
    "141": "win",
    "115": "loss",
    "235": "win"
  }
}
```

3. Committez et poussez les changements :

```bash
git add fight_results.json
git commit -m "Update fight results"
git push
```

4. Le site sera **automatiquement mis à jour** en quelques minutes via GitHub Actions !

## 🔧 Configuration GitHub Pages

1. Allez dans **Settings** → **Pages**
2. Source : **GitHub Actions**
3. Le workflow se déclenchera automatiquement

## 📝 Structure des Fichiers

```
.
├── Tirages..pdf              # PDF original avec les brackets
├── extract_fights.py         # Script d'extraction des données
├── fight_data.json           # Données extraites (généré automatiquement)
├── fight_results.json        # Résultats des combats (à mettre à jour manuellement)
├── index.html                # Site web GitHub Pages
├── parse_pdf.py              # Parser PDF initial
├── fighters_data.json        # Données des combattants (legacy)
└── .github/workflows/
    └── deploy.yml            # Workflow GitHub Actions
```

## 🎨 Fonctionnalités du Site Web

- **Vue d'ensemble** avec statistiques (combattants, combats, victoires)
- **Cartes des combattants** avec leurs informations
- **Liste complète des combats** :
  - Indicateur visuel pour les combattants du club (★)
  - Statut du combat (victoire ✓, défaite ✗, en attente)
  - Couleurs distinctives (bleu/rouge)
- **Actualisation automatique** toutes les 30 secondes
- **Design responsive** pour mobile et desktop

## 🔄 Workflow Automatique

Le système CI/CD GitHub Actions :
1. Se déclenche lors de modifications de `fight_results.json` ou `Tirages..pdf`
2. Réextrait les données du PDF
3. Génère `fight_data.json`
4. Déploie le site web mis à jour sur GitHub Pages

## 📱 Responsive Design

Le site est optimisé pour :
- 💻 Desktop
- 📱 Mobile
- 📲 Tablette

## 🎯 Comment ça marche

1. **Extraction PDF** : Le script `extract_fights.py` analyse le PDF et :
   - Trouve tous les combattants du CLUB ATHLETIQUE
   - Identifie leurs combats (numéro, adversaire, couleur)
   - Génère `fight_data.json`

2. **Mise à jour manuelle** : Vous modifiez `fight_results.json` avec les résultats

3. **Déploiement automatique** : GitHub Actions redéploie le site

4. **Visualisation** : Le site web affiche tout en temps réel

## 🏆 Exemple de Mise à Jour

Après le combat #141 (Hawa DANSOUKHO vs Lina SECIM) :

```json
{
  "fight_results": {
    "141": "win"
  }
}
```

Le site affichera immédiatement une bannière verte "✓ Victoire" pour ce combat !

## 📧 Support

Pour toute question ou problème, créez une issue sur GitHub.

---

**Bon courage à tous nos combattants ! 🥋🏆**
