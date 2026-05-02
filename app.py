"""
ImmigVision — Application Flask (VERSION CORRIGÉE)
Flask 3.x + SQLite · Tous bugs résolus
"""
import sqlite3, os, re, math
from datetime import datetime
from functools import wraps
from flask import (Flask, render_template, redirect, url_for, flash,
                   request, session, g, abort, make_response)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'immigvision-secret-key-2026-CHANGEME')
DATABASE      = os.environ.get('DATABASE_PATH', os.path.join(app.root_path, 'immigvision.db'))
SITE_NAME     = 'ImmigVision'
SITE_TAGLINE  = "Votre portail de référence sur l'immigration, les visas et les bourses"
PREVIEW_CHARS = 1200

# ── Database ─────────────────────────────────────────────────────
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db: db.close()

def query(sql, args=(), one=False):
    cur = get_db().execute(sql, args)
    rv = cur.fetchall()
    return (rv[0] if rv else None) if one else rv

def execute(sql, args=()):
    db = get_db()
    cur = db.execute(sql, args)
    db.commit()
    return cur.lastrowid

def init_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            slug TEXT UNIQUE NOT NULL,
            description TEXT DEFAULT '',
            icon TEXT DEFAULT 'fas fa-newspaper',
            color TEXT DEFAULT '#00C2CB'
        );
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            slug TEXT UNIQUE NOT NULL,
            content TEXT NOT NULL,
            excerpt TEXT DEFAULT '',
            image_url TEXT DEFAULT '',
            category_id INTEGER,
            author_id INTEGER NOT NULL,
            published INTEGER DEFAULT 0,
            featured INTEGER DEFAULT 0,
            views INTEGER DEFAULT 0,
            reading_time INTEGER DEFAULT 1,
            meta_description TEXT DEFAULT '',
            tags TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS newsletter (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            is_active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now'))
        );
    ''')
    conn.commit()

    # Catégories
    for cat in [
        ('Immigration','immigration',"Actualités immigration",'fas fa-globe-europe','#1A3A5C'),
        ('Visas','visas','Procédures et informations visas','fas fa-passport','#00C2CB'),
        ('Bourses','bourses',"Bourses d'études",'fas fa-graduation-cap','#F5A623'),
        ('Actualités','actualites','Dernières nouvelles','fas fa-newspaper','#E74C3C'),
        ('Guides','guides','Guides pratiques','fas fa-map-marked-alt','#2ECC71'),
    ]:
        c.execute('INSERT OR IGNORE INTO categories (name,slug,description,icon,color) VALUES (?,?,?,?,?)', cat)
    conn.commit()

    # Admin
    if not c.execute("SELECT id FROM users WHERE email='admin@immigvision.com'").fetchone():
        c.execute('INSERT INTO users (username,email,password_hash,is_admin) VALUES (?,?,?,?)',
                  ('admin','admin@immigvision.com',generate_password_hash('Admin@2026!'),1))
        conn.commit()

    # Articles démo
    if c.execute("SELECT COUNT(*) n FROM articles").fetchone()['n'] == 0:
        admin_id   = c.execute("SELECT id FROM users WHERE email='admin@immigvision.com'").fetchone()['id']
        cat_visa   = c.execute("SELECT id FROM categories WHERE slug='visas'").fetchone()
        cat_bourse = c.execute("SELECT id FROM categories WHERE slug='bourses'").fetchone()
        cat_imm    = c.execute("SELECT id FROM categories WHERE slug='immigration'").fetchone()
        vid = cat_visa['id'] if cat_visa else None
        bid = cat_bourse['id'] if cat_bourse else None
        iid = cat_imm['id'] if cat_imm else None

        for art in [
            ('Comment obtenir un visa de travail aux États-Unis en 2026',
             'comment-obtenir-visa-travail-etats-unis-2026',
             '''<h2>Types de visas de travail</h2>
<p>Les États-Unis proposent plusieurs catégories : <strong>H-1B</strong> (travailleurs qualifiés), <strong>L-1</strong> (transfert intraentreprise), <strong>O-1</strong> (talents extraordinaires) et les visas immigrants <strong>EB-1 à EB-5</strong>.</p>
<h2>Procédure H-1B étape par étape</h2>
<p>Votre employeur américain dépose une pétition I-129. Une fois approuvée, vous remplissez le formulaire DS-160 en ligne et passez un entretien consulaire à l'ambassade américaine la plus proche.</p>
<h2>Nouveaux frais 2025-2026</h2>
<p>La <em>Visa Integrity Fee</em> de 250 USD s'applique désormais à tous les visas non-immigrants. Les entretiens en présentiel sont obligatoires pour tous les âges depuis septembre 2025. Le frais MRV est passé de 160 à 185 USD.</p>
<h2>Documents requis</h2>
<p>Passeport valide 6 mois après le retour, photo biométrique, DS-160 imprimé, reçu de paiement MRV, I-797 (approbation pétition), lettre de l'employeur.</p>
<h2>Conseils pratiques</h2>
<p>Commencez 6 à 12 mois à l'avance. Consultez toujours un avocat spécialisé si votre situation est complexe. Vérifiez les délais actuels sur travel.state.gov.</p>''',
             'Guide complet visa travail USA 2026 : H-1B, L-1, O-1 et nouvelles règles.',
             'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&q=80',
             vid, admin_id, 1, 1, 847, 5,
             'Guide visa travail USA 2026 : H-1B, L-1, O-1 procédures',
             'visa travail,USA,H-1B,immigration 2026'),

            ("Top 10 des bourses d'études pour étudiants africains en 2026",
             'top-10-bourses-etudiants-africains-2026',
             '''<h2>1. Mastercard Foundation Scholars Program</h2>
<p>Bourse complète couvrant frais de scolarité, logement et allocation mensuelle pour les étudiants africains talentueux économiquement vulnérables.</p>
<h2>2. Bourses Erasmus Mundus</h2>
<p>Le programme européen finance des études de master dans des universités partenaires. La bourse couvre frais d'inscription, frais de vie et voyage aller-retour.</p>
<h2>3. Commonwealth Scholarships</h2>
<p>Études au Royaume-Uni pour les ressortissants des pays du Commonwealth dans presque toutes les disciplines académiques.</p>
<h2>4. Bourse Fulbright</h2>
<p>Programme américain finançant études et recherches aux USA. Disponible dans presque tous les pays africains francophones.</p>
<h2>5. Bourse de la BAD</h2>
<p>La Banque Africaine de Développement finance des masters et doctorats dans des domaines liés au développement du continent.</p>
<h2>Comment postuler avec succès</h2>
<p>Préparez votre dossier 6 mois à l'avance. Soignez votre lettre de motivation, obtenez de bonnes lettres de recommandation, maîtrisez la langue de destination.</p>''',
             "Meilleures bourses étudiants africains 2026 : guide complet.",
             'https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=800&q=80',
             bid, admin_id, 1, 1, 1243, 6,
             "Top bourses études étudiants africains 2026",
             'bourses,étudiants africains,Mastercard,Erasmus'),

            ('Immigration Canada 2026 : Express Entry et nouvelles règles',
             'immigration-canada-2026-express-entry',
             '''<h2>Comment fonctionne Express Entry ?</h2>
<p>Le système Express Entry gère les demandes de résidence permanente. Les candidats obtiennent un score CRS basé sur l'âge, niveau d'études, expérience et maîtrise des langues (anglais/français).</p>
<h2>Programmes provinciaux (PCP)</h2>
<p>Chaque province canadienne possède son propre programme avec des critères spécifiques. La Colombie-Britannique, l'Ontario et le Québec sont les destinations les plus prisées.</p>
<h2>Avantage francophone</h2>
<p>Les candidats maîtrisant le français bénéficient d'avantages significatifs, notamment le Programme francophone hors Québec et des points CRS supplémentaires.</p>
<h2>Améliorer votre score CRS</h2>
<p>Obtenez une offre d'emploi canadienne (+200 points), une nomination provinciale (+600 points), ou améliorez vos scores IELTS/TEF. Chaque point compte dans cette compétition.</p>''',
             'Nouvelles règles immigration Canada 2026 : Express Entry, PCP, programme francophone.',
             'https://images.unsplash.com/photo-1517935706615-2717063c2225?w=800&q=80',
             iid, admin_id, 1, 0, 532, 4,
             'Immigration Canada 2026 : Express Entry, résidence permanente',
             'Canada,immigration,Express Entry,résidence permanente'),

            ('Visa Schengen 2026 : procédure complète et documents requis',
             'visa-schengen-2026-procedure-complete',
             '''<h2>Qu\'est-ce que le visa Schengen ?</h2>
<p>Le visa Schengen autorise à voyager dans les 27 pays de l'espace Schengen pour 90 jours maximum sur 180 jours. Il couvre France, Allemagne, Espagne, Italie, Belgique, Pays-Bas et bien d'autres.</p>
<h2>Documents obligatoires</h2>
<p>Passeport valide 3 mois après la date de retour, formulaire de demande CERFA, 2 photos biométriques récentes, assurance voyage (minimum 30 000 €), justificatifs d'hébergement, billets d'avion et ressources financières.</p>
<h2>Frais en 2026</h2>
<p>Les frais consulaires s'élèvent à 90 € pour les adultes, 45 € pour les enfants de 6 à 12 ans, gratuit pour les moins de 6 ans. Les délais de traitement varient de 15 jours à 2 mois.</p>
<h2>Conseils pour éviter le refus</h2>
<p>Montrez des liens solides avec votre pays (emploi, famille, propriété). Prouvez votre capacité financière et préparez un itinéraire détaillé et cohérent.</p>''',
             'Guide complet visa Schengen 2026 : documents, frais et conseils pratiques.',
             'https://images.unsplash.com/photo-1467269204594-9661b134dd2b?w=800&q=80',
             vid, admin_id, 1, 0, 389, 4,
             'Visa Schengen 2026 : procédure documents frais consulaires',
             'visa Schengen,Europe,tourisme,procédure visa'),
        ]:
            c.execute('''INSERT OR IGNORE INTO articles
                (title,slug,content,excerpt,image_url,category_id,author_id,
                 published,featured,views,reading_time,meta_description,tags)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)''', art)
        conn.commit()
    conn.close()

# ── Helpers ──────────────────────────────────────────────────────
def slugify(t):
    t = t.lower().strip()
    for p,r in [('[àáâãäåā]','a'),('[èéêëē]','e'),('[ìíîïī]','i'),
                ('[òóôõöō]','o'),('[ùúûüū]','u'),('[ñ]','n'),('[ç]','c')]:
        t = re.sub(p,r,t)
    t = re.sub(r'[^a-z0-9\s-]','',t)
    t = re.sub(r'[\s_]+','-',t)
    return re.sub(r'-+','-',t).strip('-')

def strip_html(h): return re.sub(r'<[^>]+>','',h or '')
def reading_time(c): return max(1,math.ceil(len(strip_html(c).split())/200))
def get_preview(c, n=PREVIEW_CHARS):
    s = strip_html(c)
    if len(s)<=n: return s,False
    return s[:n].rsplit(' ',1)[0]+'...',True
def unique_slug(b):
    s,i=b,1
    while query('SELECT id FROM articles WHERE slug=?',[s],one=True):
        s=f'{b}-{i}';i+=1
    return s

def login_required(f):
    @wraps(f)
    def d(*a,**k):
        if not session.get('user_id'):
            flash("Connectez-vous pour accéder à cette page.",'warning')
            return redirect(url_for('login',next=request.url))
        return f(*a,**k)
    return d

def admin_required(f):
    @wraps(f)
    def d(*a,**k):
        if not session.get('user_id'):
            return redirect(url_for('login',next=request.url))
        u=query('SELECT is_admin FROM users WHERE id=? AND is_active=1',[session['user_id']],one=True)
        if not u or not u['is_admin']: abort(403)
        return f(*a,**k)
    return d

@app.context_processor
def inject_globals():
    user=None
    if session.get('user_id'):
        user=query('SELECT * FROM users WHERE id=? AND is_active=1',[session['user_id']],one=True)
        if not user: session.clear()
    cats  = query('SELECT * FROM categories ORDER BY name')
    recnt = query('''SELECT a.*,c.name cat_name,c.slug cat_slug,c.color cat_color
                     FROM articles a LEFT JOIN categories c ON a.category_id=c.id
                     WHERE a.published=1 ORDER BY a.created_at DESC LIMIT 5''')
    return dict(current_user=user, all_categories=cats, recent_articles=recnt,
                site_name=SITE_NAME, site_tagline=SITE_TAGLINE,
                current_year=datetime.now().year)

@app.template_filter('datefmt')
def datefmt(s,fmt='%d %B %Y'):
    try: return datetime.strptime(str(s)[:19],'%Y-%m-%d %H:%M:%S').strftime(fmt)
    except: return str(s)

@app.template_filter('strip_tags')
def strip_tags_f(s): return strip_html(s)

# ══════════════════════════════════════════════════════════════════
#  ROUTES PUBLIQUES
# ══════════════════════════════════════════════════════════════════
@app.route('/')
def index():
    featured=query('''SELECT a.*,c.name cat_name,c.slug cat_slug,c.color cat_color,u.username author_name
                      FROM articles a LEFT JOIN categories c ON a.category_id=c.id
                      LEFT JOIN users u ON a.author_id=u.id
                      WHERE a.published=1 AND a.featured=1 ORDER BY a.created_at DESC LIMIT 3''')
    latest=query('''SELECT a.*,c.name cat_name,c.slug cat_slug,c.color cat_color,u.username author_name
                    FROM articles a LEFT JOIN categories c ON a.category_id=c.id
                    LEFT JOIN users u ON a.author_id=u.id
                    WHERE a.published=1 ORDER BY a.created_at DESC LIMIT 12''')
    stats={
        'articles': query('SELECT COUNT(*) n FROM articles WHERE published=1',one=True)['n'],
        'users':    query('SELECT COUNT(*) n FROM users',one=True)['n'],
        'cats':     query('SELECT COUNT(*) n FROM categories',one=True)['n'],
    }
    return render_template('index.html',featured=featured,latest=latest,stats=stats)

@app.route('/article/<slug>')
def article(slug):
    art=query('''SELECT a.*,c.name cat_name,c.slug cat_slug,c.color cat_color,u.username author_name
                 FROM articles a LEFT JOIN categories c ON a.category_id=c.id
                 LEFT JOIN users u ON a.author_id=u.id
                 WHERE a.slug=? AND a.published=1''',[slug],one=True)
    if not art: abort(404)
    execute('UPDATE articles SET views=views+1 WHERE slug=?',[slug])
    is_logged=bool(session.get('user_id'))
    preview,needspw=get_preview(art['content'])
    show_paywall=needspw and not is_logged
    related=query('''SELECT a.*,c.name cat_name,c.color cat_color FROM articles a
                     LEFT JOIN categories c ON a.category_id=c.id
                     WHERE a.published=1 AND a.id!=? AND a.category_id=?
                     ORDER BY a.created_at DESC LIMIT 3''',[art['id'],art['category_id']])
    tags=[t.strip() for t in (art['tags'] or '').split(',') if t.strip()]
    return render_template('article.html',article=art,preview_text=preview,
                           show_paywall=show_paywall,is_logged=is_logged,related=related,tags=tags)

@app.route('/categorie/<slug>')
def category(slug):
    cat=query('SELECT * FROM categories WHERE slug=?',[slug],one=True)
    if not cat: abort(404)
    page,pp=request.args.get('page',1,type=int),9
    arts=query('''SELECT a.*,c.name cat_name,c.color cat_color,u.username author_name
                  FROM articles a LEFT JOIN categories c ON a.category_id=c.id
                  LEFT JOIN users u ON a.author_id=u.id
                  WHERE a.published=1 AND a.category_id=?
                  ORDER BY a.created_at DESC LIMIT ? OFFSET ?''',[cat['id'],pp,(page-1)*pp])
    total=query('SELECT COUNT(*) n FROM articles WHERE published=1 AND category_id=?',[cat['id']],one=True)['n']
    return render_template('category.html',cat=cat,articles=arts,
                           page=page,total_pages=math.ceil(total/pp))

@app.route('/recherche')
def search():
    q=request.args.get('q','').strip()
    arts=[]
    if q:
        like=f'%{q}%'
        arts=query('''SELECT a.*,c.name cat_name,c.color cat_color,u.username author_name
                      FROM articles a LEFT JOIN categories c ON a.category_id=c.id
                      LEFT JOIN users u ON a.author_id=u.id
                      WHERE a.published=1 AND (a.title LIKE ? OR a.excerpt LIKE ? OR a.tags LIKE ?)
                      ORDER BY a.created_at DESC LIMIT 20''',[like,like,like])
    return render_template('search.html',articles=arts,q=q)

@app.route('/newsletter',methods=['POST'])
def newsletter():
    email=request.form.get('email','').strip().lower()
    if not email or '@' not in email:
        flash('Adresse email invalide.','danger')
    elif query('SELECT id FROM newsletter WHERE email=?',[email],one=True):
        flash('Vous êtes déjà inscrit(e) !','info')
    else:
        execute('INSERT INTO newsletter (email) VALUES (?)',[email])
        flash('Merci ! Vous êtes inscrit(e) à la newsletter.','success')
    return redirect(request.referrer or url_for('index'))

# ── Auth ─────────────────────────────────────────────────────────
@app.route('/inscription',methods=['GET','POST'])
def register():
    if session.get('user_id'): return redirect(url_for('index'))
    if request.method=='POST':
        username=request.form.get('username','').strip()
        email=request.form.get('email','').strip().lower()
        password=request.form.get('password','')
        confirm=request.form.get('confirm_password','')
        errors=[]
        if len(username)<3: errors.append("Nom d'utilisateur : 3 caractères minimum.")
        if '@' not in email: errors.append("Adresse email invalide.")
        if len(password)<8: errors.append("Mot de passe : 8 caractères minimum.")
        if password!=confirm: errors.append("Les mots de passe ne correspondent pas.")
        if query('SELECT id FROM users WHERE email=?',[email],one=True): errors.append("Email déjà utilisé.")
        if query('SELECT id FROM users WHERE username=?',[username],one=True): errors.append("Nom d'utilisateur déjà pris.")
        if errors:
            for e in errors: flash(e,'danger')
        else:
            uid=execute('INSERT INTO users (username,email,password_hash) VALUES (?,?,?)',
                        [username,email,generate_password_hash(password)])
            session.permanent=True
            session['user_id']=uid; session['username']=username; session['is_admin']=False
            flash(f'Bienvenue {username} !','success')
            nxt=request.args.get('next','')
            return redirect(nxt if nxt and nxt.startswith('/') else url_for('index'))
    return render_template('auth/register.html')

@app.route('/connexion',methods=['GET','POST'])
def login():
    if session.get('user_id'): return redirect(url_for('index'))
    if request.method=='POST':
        email=request.form.get('email','').strip().lower()
        password=request.form.get('password','')
        user=query('SELECT * FROM users WHERE email=? AND is_active=1',[email],one=True)
        if user and check_password_hash(user['password_hash'],password):
            session.permanent=True
            session['user_id']=user['id']; session['username']=user['username']
            session['is_admin']=bool(user['is_admin'])
            flash(f"Bienvenue {user['username']} !",'success')
            nxt=request.args.get('next','')
            return redirect(nxt if nxt and nxt.startswith('/') else url_for('index'))
        flash('Email ou mot de passe incorrect.','danger')
    return render_template('auth/login.html')

@app.route('/deconnexion')
def logout():
    session.clear()
    flash('Vous avez été déconnecté(e).','info')
    return redirect(url_for('index'))

# ── Admin ─────────────────────────────────────────────────────────
@app.route('/admin')
@admin_required
def admin_dashboard():
    stats={
        'articles_total': query('SELECT COUNT(*) n FROM articles',one=True)['n'],
        'articles_pub':   query('SELECT COUNT(*) n FROM articles WHERE published=1',one=True)['n'],
        'users_total':    query('SELECT COUNT(*) n FROM users',one=True)['n'],
        'newsletter_total':query('SELECT COUNT(*) n FROM newsletter WHERE is_active=1',one=True)['n'],
        'total_views':    query('SELECT COALESCE(SUM(views),0) n FROM articles',one=True)['n'],
    }
    recent_articles=query('''SELECT a.*,c.name cat_name,u.username author_name
                              FROM articles a LEFT JOIN categories c ON a.category_id=c.id
                              LEFT JOIN users u ON a.author_id=u.id
                              ORDER BY a.created_at DESC LIMIT 8''')
    recent_users=query('SELECT * FROM users ORDER BY created_at DESC LIMIT 6')
    top_articles=query('''SELECT a.*,c.name cat_name FROM articles a
                          LEFT JOIN categories c ON a.category_id=c.id
                          WHERE a.published=1 ORDER BY a.views DESC LIMIT 5''')
    return render_template('admin/dashboard.html',stats=stats,
                           recent_articles=recent_articles,
                           recent_users=recent_users,top_articles=top_articles)

@app.route('/admin/articles')
@admin_required
def admin_articles():
    page,pp=request.args.get('page',1,type=int),15
    cf=request.args.get('cat',''); sf=request.args.get('status','')
    where,args='WHERE 1=1',[]
    if cf: where+=' AND a.category_id=?'; args.append(cf)
    if sf=='published': where+=' AND a.published=1'
    elif sf=='draft':   where+=' AND a.published=0'
    arts=query(f'''SELECT a.*,c.name cat_name,u.username author_name
                   FROM articles a LEFT JOIN categories c ON a.category_id=c.id
                   LEFT JOIN users u ON a.author_id=u.id
                   {where} ORDER BY a.created_at DESC LIMIT ? OFFSET ?''',
               args+[pp,(page-1)*pp])
    total=query(f'SELECT COUNT(*) n FROM articles a {where}',args,one=True)['n']
    cats=query('SELECT * FROM categories ORDER BY name')
    return render_template('admin/articles.html',articles=arts,categories=cats,
                           page=page,total_pages=math.ceil(total/pp),
                           cat_filter=cf,status_filter=sf)

@app.route('/admin/articles/nouveau',methods=['GET','POST'])
@admin_required
def admin_article_new():
    cats=query('SELECT * FROM categories ORDER BY name')
    if request.method=='POST':
        title=request.form.get('title','').strip()
        content=request.form.get('content','').strip()
        if not title or not content:
            flash('Titre et contenu obligatoires.','danger')
        else:
            excerpt=request.form.get('excerpt','').strip() or strip_html(content)[:300]+'...'
            execute('''INSERT INTO articles
                (title,slug,content,excerpt,image_url,category_id,author_id,
                 published,featured,reading_time,meta_description,tags)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''',
                [title, unique_slug(slugify(title)), content, excerpt,
                 request.form.get('image_url','').strip(),
                 request.form.get('category_id') or None, session['user_id'],
                 1 if request.form.get('published') else 0,
                 1 if request.form.get('featured') else 0,
                 reading_time(content),
                 request.form.get('meta_description','').strip(),
                 request.form.get('tags','').strip()])
            flash('Article créé !','success')
            return redirect(url_for('admin_articles'))
    return render_template('admin/article_form.html',categories=cats,article=None)

@app.route('/admin/articles/<int:aid>/modifier',methods=['GET','POST'])
@admin_required
def admin_article_edit(aid):
    art=query('SELECT * FROM articles WHERE id=?',[aid],one=True)
    if not art: abort(404)
    cats=query('SELECT * FROM categories ORDER BY name')
    if request.method=='POST':
        title=request.form.get('title','').strip()
        content=request.form.get('content','').strip()
        if not title or not content:
            flash('Titre et contenu obligatoires.','danger')
        else:
            excerpt=request.form.get('excerpt','').strip() or strip_html(content)[:300]+'...'
            execute('''UPDATE articles SET title=?,content=?,excerpt=?,image_url=?,
                       category_id=?,published=?,featured=?,reading_time=?,
                       meta_description=?,tags=?,updated_at=datetime('now') WHERE id=?''',
                    [title,content,excerpt,
                     request.form.get('image_url','').strip(),
                     request.form.get('category_id') or None,
                     1 if request.form.get('published') else 0,
                     1 if request.form.get('featured') else 0,
                     reading_time(content),
                     request.form.get('meta_description','').strip(),
                     request.form.get('tags','').strip(), aid])
            flash('Article mis à jour !','success')
            return redirect(url_for('admin_articles'))
    return render_template('admin/article_form.html',categories=cats,article=art)

@app.route('/admin/articles/<int:aid>/supprimer',methods=['POST'])
@admin_required
def admin_article_delete(aid):
    execute('DELETE FROM articles WHERE id=?',[aid])
    flash('Article supprimé.','info')
    return redirect(url_for('admin_articles'))

@app.route('/admin/articles/<int:aid>/toggle',methods=['POST'])
@admin_required
def admin_article_toggle(aid):
    art=query('SELECT published FROM articles WHERE id=?',[aid],one=True)
    if art: execute('UPDATE articles SET published=? WHERE id=?',[1-art['published'],aid])
    return redirect(url_for('admin_articles'))

@app.route('/admin/utilisateurs')
@admin_required
def admin_users():
    return render_template('admin/users.html',
                           users=query('SELECT * FROM users ORDER BY created_at DESC'),
                           newsletter_subs=query('SELECT * FROM newsletter WHERE is_active=1 ORDER BY created_at DESC'))

@app.route('/admin/utilisateurs/<int:uid>/toggle-admin',methods=['POST'])
@admin_required
def admin_toggle_admin(uid):
    if uid==session['user_id']:
        flash('Impossible de modifier votre propre statut.','warning')
    else:
        u=query('SELECT is_admin FROM users WHERE id=?',[uid],one=True)
        if u: execute('UPDATE users SET is_admin=? WHERE id=?',[1-u['is_admin'],uid])
        flash('Statut modifié.','success')
    return redirect(url_for('admin_users'))

@app.route('/admin/utilisateurs/<int:uid>/supprimer',methods=['POST'])
@admin_required
def admin_delete_user(uid):
    if uid==session['user_id']:
        flash('Impossible de supprimer votre propre compte.','danger')
    else:
        execute('DELETE FROM users WHERE id=?',[uid]); flash('Utilisateur supprimé.','info')
    return redirect(url_for('admin_users'))

# ── SEO ──────────────────────────────────────────────────────────
@app.route('/sitemap.xml')
def sitemap():
    arts=query('SELECT slug,updated_at FROM articles WHERE published=1')
    cats=query('SELECT slug FROM categories')
    base=request.url_root.rstrip('/')
    xml=['<?xml version="1.0" encoding="UTF-8"?>',
         '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for p in ['/','/connexion','/inscription']:
        xml.append(f'<url><loc>{base}{p}</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>')
    for c in cats:
        xml.append(f'<url><loc>{base}/categorie/{c["slug"]}</loc><changefreq>daily</changefreq><priority>0.7</priority></url>')
    for a in arts:
        d=(a['updated_at'] or '')[:10]
        xml.append(f'<url><loc>{base}/article/{a["slug"]}</loc><lastmod>{d}</lastmod><changefreq>monthly</changefreq><priority>0.9</priority></url>')
    xml.append('</urlset>')
    r=make_response('\n'.join(xml)); r.headers['Content-Type']='application/xml'; return r

@app.route('/robots.txt')
def robots():
    base=request.url_root.rstrip('/')
    r=make_response(f"User-agent: *\nAllow: /\nDisallow: /admin\nSitemap: {base}/sitemap.xml\n")
    r.headers['Content-Type']='text/plain'; return r

@app.errorhandler(404)
def e404(e): return render_template('errors/404.html'),404
@app.errorhandler(403)
def e403(e): return render_template('errors/403.html'),403
@app.errorhandler(500)
def e500(e): return render_template('errors/500.html'),500

with app.app_context():
    init_db()

if __name__=='__main__':
    port=int(os.environ.get('PORT',5000))
    debug=os.environ.get('FLASK_DEBUG','false').lower()=='true'
    print(f"\n  🌍 ImmigVision → http://localhost:{port}")
    print(f"  🔐 Admin → http://localhost:{port}/admin")
    print(f"  📧 admin@immigvision.com  |  🔑 Admin@2026!\n")
    app.run(host='0.0.0.0',port=port,debug=debug)
