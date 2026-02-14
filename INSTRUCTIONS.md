# Instructions pour Mettre à Jour les Résultats des Combats

## Méthode Simple (via GitHub Web Interface)

1. Allez sur GitHub : https://github.com/bcoeugnet/Extract-Fight-TKD
2. Cliquez sur le fichier `fight_results.json`
3. Cliquez sur l'icône crayon (✏️) pour éditer
4. Ajoutez les résultats des combats terminés dans la section `"fight_results"` :

```json
{
  "fight_results": {
    "141": "win",
    "115": "loss",
    "235": "win"
  },
  ...
}
```

5. Faites défiler vers le bas et cliquez sur "Commit changes"
6. Attendez 2-3 minutes : le site sera automatiquement mis à jour !

## Résultats Possibles

- `"win"` = Victoire ✓ (bannière verte)
- `"loss"` = Défaite ✗ (bannière rouge)

## Exemple Complet

Si CHERINE FAKKOUL (Combat #117) a gagné et ABDEL SALAM DJABRI (Combat #145) a perdu :

```json
{
  "fight_results": {
    "117": "win",
    "145": "loss"
  },
  "comments": {
    "instructions": "Update fight results by adding entries like: 'fight_number': 'win' or 'loss'",
    "example": {
      "141": "win",
      "235": "loss"
    }
  }
}
```

## Notes

- Le numéro de combat est celui affiché sur le site et dans le PDF
- Vous pouvez ajouter plusieurs résultats à la fois
- Le site se met à jour automatiquement via GitHub Actions
- Les visiteurs verront les changements après 2-3 minutes

## Voir le Site Web

Une fois GitHub Pages activé, le site sera disponible à :
```
https://bcoeugnet.github.io/Extract-Fight-TKD/
```

## Activation de GitHub Pages

1. Allez dans **Settings** (Paramètres) → **Pages**
2. Sous "Build and deployment" :
   - Source: **GitHub Actions**
3. Le site se déploiera automatiquement après le premier commit sur la branche `main`
