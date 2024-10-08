import json
import frappe
from frappe import auth

#Authenticate and Login to ERPNext With an API
@frappe.whitelist( allow_guest=True )
def authentication_api(usr, pwd):
    try:
        login_manager = frappe.auth.LoginManager()
        login_manager.authenticate(user=usr, pwd=pwd)
        login_manager.post_login()
    except frappe.exceptions.AuthenticationError:
        frappe.clear_messages()
        frappe.local.response["message"] = {
            "success_key":0,
            "message":"Authentication Error!"
        }

        return

    api_generate = generate_keys(frappe.session.user)
    user = frappe.get_doc('User', frappe.session.user)

    frappe.response["message"] = {
        "success_key":1,
        "message":"Authentication success",
        "sid":frappe.session.sid,
        "api_key":user.api_key,
        "api_secret":api_generate,
        "token": "token"+" "+user.api_key+":"+api_generate,
        "username":user.username,
        "email":user.email,
        "mobile_no":user.mobile_no,
        "phone":user.phone
    }

def generate_keys(user):
    user_details = frappe.get_doc('User', user)
    api_secret = frappe.generate_hash(length=15)

    if not user_details.api_key:
        api_key = frappe.generate_hash(length=15)
        user_details.api_key = api_key

    user_details.api_secret = api_secret
    user_details.save()

    return api_secret

@frappe.whitelist(allow_guest=True)
def logout():
    try:
        login_manager = frappe.auth.LoginManager()
        user = frappe.session.user
        # login_manager = LoginManager()
        login_manager.logout(user=user)
        # return generate_response("S", "200", message="Logged Out")
        return "Logout"
    except Exception as e:
        raise Exception(e)
def manage_user():
    args = json.loads(frappe.form_dict.args)
    sid = args.get('sid')

    if not sid:
        raise Exception("sid not provided")

    else:
        try:
            frappe.form_dict["sid"] = sid 
            loginmgr = frappe.auth.LoginManager()
            return True
        except:
            raise Exception(e.message)