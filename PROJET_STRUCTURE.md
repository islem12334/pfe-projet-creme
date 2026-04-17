# Structure Détaillée Projet \"projet_creme\" - Gestion Stock & Production (Version Étendue)

Date: {{ current_date }}

## 1. Aperçu Général
- **Nom** : projet_creme
- **Type** : Application web Django 6.0.2
- **Objectif** : Système SaaS de gestion de stock matières premières et suivi production industrielle (3 shifts).
- **Fonctionnalités clés** :
  + Gestion réceptions (fournisseurs, lots multiples, DLUO).
  + Sorties stock vers production.
  + Ouvertures production (ligne, OF, produit, qty kg, shift P1/P2/P3).
  + Dashboards/stock actuel/historique/analytics par rôle.
  + Permissions granulaires (decorateurs/middleware).
- **Base données** : SQLite (`db.sqlite3`, 6 migrations).
- **Utilisateurs** : Profils liés User (matricule unique), types : admin/magasin/production.
- **UI** : Bootstrap + saas.css (moderne, responsive).
- **Templates** : **32 fichiers HTML** (complet listé ci-dessous).

## 2. Arbre Complet Dossiers/Fichiers avec Descriptions Détaillées

```
c:/Users/poste/projet_creme/
├── db.sqlite3 (2 Mo approx)
│   Données tables : auth_user, gestion_stock_profile, fournisseur, reception, sortiestockproduction, ouvertureproduction.
├── manage.py
│   Script CLI Django : runserver, migrate, collectstatic, createsuperuser.
├── TODO.md
│   Tâches en cours développement.
├── gestion_stock/  (**Cœur métier - 100+ fichiers**)
│   ├── __init__.py / apps.py (GestionStockConfig)
│   ├── admin.py (ProfileAdmin : list_display matricule/nom/type)
│   ├── context_processors.py (role_flags pour templates)
│   ├── signals.py (hooks post-save)
│   ├── tests.py (tests unitaires)
│   ├── models.py (**5 modèles détaillés**) :
│   │   * Profile : OneToOne User, matricule(unique), type_operateur(3 choices), nom/prenom. Auto-set username=matricule.
│   │   * Fournisseur : nom(200), adresse(255), telephone(20).
│   │   * Reception : profile(FK), fournisseur(FK), date_reception(auto), lot_code1-10(50), date_expiration, quantite(Decimal10,3 default 0.500). Prop lot_reference, method lot_codes().
│   │   * SortieStockProduction : profile(FK), date_heure(auto), numero_lot(50), quantite(Decimal).
│   │   * OuvertureProduction : profile(FK), ligne_production(100), date_heure_ouverture(DTField), numero_lot(50), numero_ordre_fabrication(100), nom_produit(150), quantite, shift(2 choices P1/P2/P3).
│   ├── forms.py (**3 ModelForms personnalisées**) :
│   │   ReceptionForm, SortieStockProductionForm (init user), OuvertureProductionForm (init user).
│   ├── views.py (**~35 vues/CBVs détaillées**) :
│   │   Production (@production_required) : production() (dashboard réceptions/stock/form ouverture), data_performance(), profile_production(), stock_actuel_production(), historique(), nouvelle_production().
│   │   Magasin (@magasin_required) : dashboard(), reception CRUD (List/CreateView/UpdateView/delete/detail), transfert CRUD.
│   │   Autres : landing(), login_view() (role-redirect), utils lot_expiration_info().
│   ├── urls.py (URLs globales app : production/ namespace, magasin/, reception/, transfert/, etc. LogoutView).
│   ├── urls_production.py (namespace='production' : index, data_performance, profile/stock/historique/nouvelle_production, ouvertures new/list).
│   ├── utils.py (lot_expiration_info dict status/warning/expired).
│   ├── decorators.py (@magasin_required etc.), mixins_fixed.py (PermissionMixin/MagasinAccessMixin), middleware.py (MagasinAccessMiddleware).
│   ├── migrations/ (0001_initial.py ... 0006_alter_reception_date_reception.py).
│   ├── static/
│   │   ├── css/production-modal.css (modals prod), saas.css (thèmes SaaS).
│   │   └── images/logo.png.
│   ├── templates/ (**32 templates - listé exhaustif**) :
│   │   **28 pages principales** (extends base.html) :
│   │   - base.html (layout principal : topbar, sidebar, content).
│   │   - landing.html, login.html (auth).
│   │   - dashboard.html (magasin stats/récents).
│   │   - data_performance.html (analytics prod).
│   │   - historique.html (20 dernières ouvertures).
│   │   - production.html (dashboard prod : stock/réceptions/form).
│   │   - profile.html (magasin), profile_production.html (prod).
│   │   - nouvelle_production.html (form OuvertureProduction : UI riche hero/form/sidebar-help, champs opérateurs/ligne/date/lot/OF/produit/qty/shift).
│   │   - stock.html, stock_actuel.html (stock avec status expiry).
│   │   - reception_* : list.html, form.html, detail.html (lots list), confirm_delete.html.
│   │   - sortie_stock_* : list.html, form.html, confirm_delete.html.
│   │   - transfert_* : list.html, detail.html, confirm_delete.html.
│   │   - ouverture_production_* : list.html, form.html, confirm_delete.html.
│   │   **4 partials** (partials/) : _action_buttons.html, sidebar.html, sidebar_production.html (menu prod), topbar.html.
│   └── design_backup/ (base_saas.html, landing_original.html, saas.css, partials anciens).
├── projet_creme/ (**Configs projet global**)
│   ├── __init__.py, asgi.py, wsgi.py (déploiement).
│   └── settings.py (détaillé) :
│       INSTALLED_APPS : django.contrib.* + 'gestion_stock'.
│       MIDDLEWARE : security/session/csrf/auth + custom MagasinAccessMiddleware.
│       TEMPLATES : context_processors request/auth/messages + role_flags.
│       DATABASES : SQLite.
│       STATIC : URL/DIRS(gestion_stock/static)/ROOT(staticfiles).
│       SECURITY : CSRF_TRUSTED_ORIGINS(localhost), DEBUG env.
│       AUTH : LOGIN_URL='login'.
│   └── urls.py (racines : inclut gestion_stock.urls).
└── staticfiles/ (**collectstatic output** : admin/css/js/img + app css/images).
├── c (fichier inconnu, ignore).
└── projet_creme - Raccourci.lnk (shortcut).
```

## 3. URLs Principales (extrait)
- `/` : landing
- `/login/` : login (redirect rôle : production→index, magasin→dashboard)
- `/production/` : dashboard prod
- `/production/nouvelle/` : nouvelle production
- `/reception/` : list réceptions
- `/logout/`

## 4. Permissions Système
- Décorateurs : @production_required, @magasin_required, @admin_required.
- Mixins : LoginRequiredMixin + custom.
- Middleware : Accès magasin contrôlé.

## 5. Installation & Lancement
```
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser  # Créer admin + profils via /admin/
python manage.py collectstatic --noinput
python manage.py runserver
```
Accès : http://127.0.0.1:8000/admin (créer Profile), /production/ (login matricule).

## 6. Améliorations Possibles
- PostgreSQL prod.
- API REST (DRF).
- Charts JS (analytics).
- Export CSV/PDF.

**Document complet - Dernière MAJ : Automatique.**
