from flask import Flask, render_template, request, redirect, session, abort, send_from_directory
import mysql.connector
from werkzeug.security import check_password_hash, generate_password_hash
import os
from dotenv import load_dotenv
from pathlib import Path

# ===== LOAD ENV FILE =====
load_dotenv()
app = Flask(__name__)

# ===== DATABASE CONNECTION =====
db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    port=int(os.getenv("DB_PORT")),
    use_pure=True
)
# ===== SECURITY SETTINGS =====
app.secret_key = os.getenv("SECRET_KEY")
app.config['SESSION_COOKIE_HTTPONLY'] = True

# ===== ACTIVITY LOG =====
def log_activity(user, action, ip):
    cur = db.cursor()
    cur.execute("""
        INSERT INTO activity_logs(username,action,ip_address)
        VALUES(%s,%s,%s)
    """,(user,action,ip))
    db.commit()
    cur.close()

# ===== GLOBAL ROUTE PROTECTION =====
@app.before_request
def protect_routes():

    admin_routes = ["/add_user"]

    if request.path in admin_routes:

        if "user" not in session:
            return redirect("/")

        if session.get("role") != "admin":
            abort(403)

# ===== LOGIN =====
@app.route("/", methods=["GET","POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        cur = db.cursor(dictionary=True)
        cur.execute("SELECT password,role FROM users WHERE username=%s",(username,))
        row = cur.fetchone()
        cur.close()

        ip = request.remote_addr

        if row and check_password_hash(row["password"], password):

            session["user"] = username
            session["role"] = row["role"]

            log_activity(username,"LOGIN_SUCCESS",ip)

            return redirect("/")

        else:
            log_activity(username,"LOGIN_FAILED",ip)
            return render_template("login.html", error="Invalid Login")

    return render_template("login.html")

# ===== ADD USER (ADMIN ONLY) =====
@app.route("/add_user", methods=["GET","POST"])
def add_user():

    if request.method == "POST":

        username = request.form["username"]
        password = generate_password_hash(
            request.form["password"],
            method="pbkdf2:sha256"
        )

        cur = db.cursor()
        cur.execute(
            "INSERT INTO users(username,password,role) VALUES(%s,%s,'user')",
            (username,password)
        )
        db.commit()
        cur.close()

        log_activity(session["user"], f"CREATED_USER:{username}", request.remote_addr)

        return redirect("/")

    return render_template("add_user.html")

# ===== HANDBOOK =====
@app.route("/handbook")
def handbook():

    if "user" not in session:
        abort(403)

    log_activity(session["user"], "OPENED_HANDBOOK", request.remote_addr)
    return render_template("handbook.html")

@app.route("/bms-iot")
def bms_iot():
    if "user" not in session:
        abort(403)
    
    log_activity(session["user"], "OPENED_BMS_IOT_MANUAL", request.remote_addr)
    
    try:
        return send_from_directory('static/BMS_IOT', 'bms_iot.html')
    except Exception as e:
        print(f"Error serving BMS IoT manual: {e}")
        return f"Error: Could not find 'bms_iot.html' in 'static/BMS_IOT/' folder. Error details: {str(e)}", 404
# ===== JBM ROUTES =====
@app.route("/jbm-gocc")
def jbm_gocc():
    if "user" not in session:
        abort(403)
    
    try:
        # Try to serve the file from static/jbm_gocc/
        return send_from_directory('static/jbm_gocc', 'gocc_arch_2.html')
    except Exception as e:
        # Log the error and return a helpful message
        print(f"Error serving JBM GOCC file: {e}")
        return f"Error: Could not find the file. Make sure 'gocc_arch_2.html' exists in 'static/jbm_gocc/' folder. Error details: {str(e)}", 404

@app.route("/jbm-group")
def jbm_group():
    if "user" not in session:
        abort(403)
    
    try:
        # Try to serve the file from static/jbm_group_login/
        return send_from_directory('static/jbm_group', 'Login.html')
    except Exception as e:
        # Log the error and return a helpful message
        print(f"Error serving JBM Group file: {e}")
        return f"Error: Could not find the file. Make sure 'Login.html' exists in 'static/jbm_group/' folder. Error details: {str(e)}", 404

# ===== ALM ROUTES =====
@app.route("/alm")
def alm_home():
    if "user" not in session:
        abort(403)
    
    try:
        # Serve the main ALM index file from static/ALM/
        return send_from_directory('static/ALM', 'index.html')
    except Exception as e:
        print(f"Error serving ALM home: {e}")
        return f"Error: Could not find 'index.html' in 'static/ALM/' folder. Error details: {str(e)}", 404

@app.route("/alm-docs")
def alm_docs():
    if "user" not in session:
        abort(403)
    
    try:
        return send_from_directory('static/ALM', 'docs.html')
    except Exception as e:
        print(f"Error serving ALM docs: {e}")
        return f"Error: Could not find 'docs.html' in 'static/ALM/' folder. Error details: {str(e)}", 404

@app.route("/alm-architecture")
def alm_architecture():
    if "user" not in session:
        abort(403)
    
    try:
        return send_from_directory('static/ALM', 'architecture_index.html')
    except Exception as e:
        print(f"Error serving ALM architecture: {e}")
        return f"Error: Could not find 'architecture.html' in 'static/ALM/' folder. Error details: {str(e)}", 404


# ===== ALM ARCHITECTURE SUB-ROUTES =====
@app.route("/alm-architecture/technical")
def alm_architecture_technical():
    if "user" not in session:
        abort(403)
    try:
        return send_from_directory('static/ALM', 'arch_1.html')
    except Exception as e:
        print(f"Error serving technical architecture: {e}")
        return f"Error: Could not find 'arch_1.html' in 'static/ALM/' folder. Error details: {str(e)}", 404

@app.route("/alm-architecture/governance")
def alm_architecture_governance():
    if "user" not in session:
        abort(403)
    try:
        return send_from_directory('static/ALM', 'arch_2.html')
    except Exception as e:
        print(f"Error serving governance model: {e}")
        return f"Error: Could not find 'arch_2.html' in 'static/ALM/' folder. Error details: {str(e)}", 404

@app.route("/alm-architecture/conversation")
def alm_architecture_conversation():
    if "user" not in session:
        abort(403)
    try:
        return send_from_directory('static/ALM', 'arch_3.html')
    except Exception as e:
        print(f"Error serving design conversation: {e}")
        return f"Error: Could not find 'arch_3.html' in 'static/ALM/' folder. Error details: {str(e)}", 404

@app.route("/alm-architecture/master")
def alm_architecture_master():
    if "user" not in session:
        abort(403)
    try:
        return send_from_directory('static/ALM', 'arch_4.html')
    except Exception as e:
        print(f"Error serving master document: {e}")
        return f"Error: Could not find 'arch_4.html' in 'static/ALM/' folder. Error details: {str(e)}", 404
@app.route("/alm-database")
def alm_database():
    if "user" not in session:
        abort(403)
    
    try:
        return send_from_directory('static/ALM', 'database.html')
    except Exception as e:
        print(f"Error serving ALM database: {e}")
        return f"Error: Could not find 'database.html' in 'static/ALM/' folder. Error details: {str(e)}", 404

# ===== ALM FRONTEND SUB-ROUTES =====
@app.route("/alm-frontend/access-security")
def alm_frontend_access_security():
    if "user" not in session:
        abort(403)
    try:
        return send_from_directory('static/ALM', 'UI_access_security.html')
    except Exception as e:
        print(f"Error serving access security: {e}")
        return f"Error: Could not find file. Error details: {str(e)}", 404

@app.route("/alm-frontend/asset-product")
def alm_frontend_asset_product():
    if "user" not in session:
        abort(403)
    try:
        return send_from_directory('static/ALM', 'frontend_asset_product.html')
    except Exception as e:
        print(f"Error serving asset product: {e}")
        return f"Error: Could not find file. Error details: {str(e)}", 404


@app.route("/alm-frontend/asset-product/fleet-dashboard")
def alm_frontend_fleet_dashboard():
    if "user" not in session:
        abort(403)
    try:
        return send_from_directory('static/ALM', 'frontend_fleet_dashboard.html')
    except Exception as e:
        print(f"Error serving fleet dashboard: {e}")
        return f"Error: Could not find file. Error details: {str(e)}", 404

@app.route("/alm-frontend/asset-product/workspace-assets")
def alm_frontend_workspace_assets():
    if "user" not in session:
        abort(403)
    try:
        return send_from_directory('static/ALM', 'frontend_workspace_assets.html')
    except Exception as e:
        print(f"Error serving workspace assets: {e}")
        return f"Error: Could not find file. Error details: {str(e)}", 404

@app.route("/alm-frontend/auth-roles")
def alm_frontend_auth_roles():
    if "user" not in session:
        abort(403)
    try:
        return send_from_directory('static/ALM', 'frontend_auth_roles.html')
    except Exception as e:
        print(f"Error serving auth roles: {e}")
        return f"Error: Could not find file. Error details: {str(e)}", 404

@app.route("/alm-frontend/dashboards")
def alm_frontend_dashboards():
    if "user" not in session:
        abort(403)
    try:
        return send_from_directory('static/ALM', 'UI_Workspace_dashboard.html')
    except Exception as e:
        print(f"Error serving dashboards: {e}")
        return f"Error: Could not find file. Error details: {str(e)}", 404

@app.route("/alm-frontend/onboarding")
def alm_frontend_onboarding():
    if "user" not in session:
        abort(403)
    try:
        return send_from_directory('static/ALM', 'UI_onboarding.html')
    except Exception as e:
        print(f"Error serving onboarding: {e}")
        return f"Error: Could not find file. Error details: {str(e)}", 404

@app.route("/alm-frontend/operations")
def alm_frontend_operations():
    if "user" not in session:
        abort(403)
    try:
        return send_from_directory('static/ALM', 'UI_operations.html')
    except Exception as e:
        print(f"Error serving operations: {e}")
        return f"Error: Could not find file. Error details: {str(e)}", 404

@app.route("/alm-frontend/ui-concepts")
def alm_frontend_ui_concepts():
    if "user" not in session:
        abort(403)
    try:
        return send_from_directory('static/ALM', 'UI_concepts.html')
    except Exception as e:
        print(f"Error serving UI concepts: {e}")
        return f"Error: Could not find file. Error details: {str(e)}", 404

@app.route("/alm-frontend/workspace")
def alm_frontend_workspace():
    if "user" not in session:
        abort(403)
    try:
        return send_from_directory('static/ALM', 'UI_workspace.html')
    except Exception as e:
        print(f"Error serving workspace: {e}")
        return f"Error: Could not find file. Error details: {str(e)}", 404

@app.route("/alm-documents")
def alm_documents():
    if "user" not in session:
        abort(403)
    
    try:
        return send_from_directory('static/ALM', 'documents.html')
    except Exception as e:
        print(f"Error serving ALM documents: {e}")
        return f"Error: Could not find 'documents.html' in 'static/ALM/' folder. Error details: {str(e)}", 404

@app.route("/alm-documents/download")
def alm_documents_download():
    if "user" not in session:
        abort(403)
    
    try:
        # Log the download activity
        log_activity(session["user"], "DOWNLOADED_ALM_DOCUMENTS", request.remote_addr)
        
        # Send the zip file for download directly from static/ALM folder
        return send_from_directory(
            'static/ALM', 
            'Documents.zip',
            as_attachment=True,
            download_name='ALM_Documentation_Package.zip'
        )
    except Exception as e:
        print(f"Error serving ALM documents download: {e}")
        return f"Error: Could not find 'Documents.zip' in 'static/ALM/' folder. Error details: {str(e)}", 404

@app.route("/alm-frontend")
def alm_frontend():
    if "user" not in session:
        abort(403)
    
    try:
        return send_from_directory('static/ALM', 'frontend.html')
    except Exception as e:
        print(f"Error serving ALM frontend: {e}")
        return f"Error: Could not find 'frontend.html' in 'static/ALM/' folder. Error details: {str(e)}", 404

@app.route("/alm-process")
def alm_process():
    if "user" not in session:
        abort(403)
    
    try:
        return send_from_directory('static/ALM', 'process_index.html')
    except Exception as e:
        print(f"Error serving ALM process: {e}")
        return f"Error: Could not find 'process_index.html' in 'static/ALM/' folder. Error details: {str(e)}", 404

# ===== ALM PROCESS SUB-ROUTES =====
@app.route("/alm-process/interactive-demo")
def alm_process_demo():
    if "user" not in session:
        abort(403)
    
    try:
        return send_from_directory('static/ALM', 'alm_interactive_demo.html')
    except Exception as e:
        print(f"Error serving interactive demo: {e}")
        return f"Error: Could not find file. Error details: {str(e)}", 404

@app.route("/alm-process/architecture-decisions")
def alm_process_decisions():
    if "user" not in session:
        abort(403)
    
    try:
        return send_from_directory('static/ALM', 'alm_architecture_decisions.html')
    except Exception as e:
        print(f"Error serving architecture decisions: {e}")
        return f"Error: Could not find file. Error details: {str(e)}", 404

@app.route("/alm-product")
def alm_product():
    if "user" not in session:
        abort(403)
    
    try:
        return send_from_directory('static/ALM', 'alm_marketing_1.html')
    except Exception as e:
        print(f"Error serving ALM product: {e}")
        return f"Error: Could not find 'product_index.html' in 'static/ALM/' folder. Error details: {str(e)}", 404





@app.route("/alm-research")
def alm_research():
    if "user" not in session:
        abort(403)
    
    try:
        return send_from_directory('static/ALM', 'research_index.html')
    except Exception as e:
        print(f"Error serving ALM research: {e}")
        return f"Error: Could not find 'research_index.html' in 'static/ALM/' folder. Error details: {str(e)}", 404

# ===== ALM RESEARCH SUB-ROUTES =====
@app.route("/alm-research/complete-documentation")
def alm_research_complete():
    if "user" not in session:
        abort(403)
    
    try:
        return send_from_directory('static/ALM', 'alm_complete_documentation.html')
    except Exception as e:
        print(f"Error serving complete documentation: {e}")
        return f"Error: Could not find file. Error details: {str(e)}", 404

@app.route("/alm-research/conversation-thread")
def alm_research_conversation():
    if "user" not in session:
        abort(403)
    
    try:
        return send_from_directory('static/ALM', 'alm_conversation_thread.html')
    except Exception as e:
        print(f"Error serving conversation thread: {e}")
        return f"Error: Could not find file. Error details: {str(e)}", 404

@app.route("/alm-research/thread-navigation")
def alm_research_navigation():
    if "user" not in session:
        abort(403)
    
    try:
        return send_from_directory('static/ALM', 'alm_thread_navigation.html')
    except Exception as e:
        print(f"Error serving thread navigation: {e}")
        return f"Error: Could not find file. Error details: {str(e)}", 404

@app.route("/alm-research/design-decisions")
def alm_research_decisions():
    if "user" not in session:
        abort(403)
    
    try:
        return send_from_directory('static/ALM', 'alm_design_decisions.html')
    except Exception as e:
        print(f"Error serving design decisions: {e}")
        return f"Error: Could not find file. Error details: {str(e)}", 404
@app.route("/iot-command")
def iot_command():
    if "user" not in session:
        abort(403)
    return render_template("iot_command.html")

# ===== LOGOUT =====
@app.route("/logout")
def logout():

    if "user" in session:
        log_activity(session["user"], "LOGOUT", request.remote_addr)

    session.clear()
    return redirect("/")

# ===== ERROR HANDLERS =====
@app.errorhandler(404)
def not_found(e):
    return "Page not found. Please check the URL.", 404

@app.errorhandler(403)
def forbidden(e):
    return "Access forbidden. Please log in.", 403

# ===== RUN =====
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
