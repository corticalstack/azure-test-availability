import streamlit as st
from streamlit.server.server import Server
from streamlit.script_run_context import add_script_run_ctx
import pandas as pd
import pyodbc
#pyodbc.drivers()

server = 'cs-test-availability-sql.database.windows.net'
database = 'cs-test-availability-sqldb'
username = 'azadmin'
password = 'BeanieBoblets123'   
driver= '{ODBC Driver 18 for SQL Server}'


class App:
    def __init__(self):
        st.set_page_config(page_title="Test Azure Availability", page_icon="src/assets/img/logo.png", layout="wide", initial_sidebar_state="auto")

        if "config_loaded" not in st.session_state:
            st.session_state.update({
                "orders": [],
                "http_headers": self._get_session_http_headers(),
            })

        if "df_results" not in st.session_state:
            self._get_orders()
            st.session_state["df_results"] = pd.DataFrame(st.session_state["orders"], columns=['OrderDate','SalesOrderNumber','PurchaseOrderNumber','CustomerID','TotalDue'])


    def _get_session_http_headers(self):
        headers = {
            "site_host": "",
            "logged_in_user_name": "",
            "site_deployment_id": ""
        }

        session_id = add_script_run_ctx().streamlit_script_run_ctx.session_id
        session_info = Server.get_current()._get_session_info(session_id)

        # Note case of headers differs from shown in xxx.scm.azurewebsites.net/env
        try:
            if "Host" in session_info.ws.request.headers._dict:
                headers["site_host"] = session_info.ws.request.headers._dict["Host"]

            if "X-Ms-Client-Principal-Name" in session_info.ws.request.headers._dict:
                headers["logged_in_user_name"] = session_info.ws.request.headers._dict["X-Ms-Client-Principal-Name"]

            if "X-Site-Deployment-Id" in session_info.ws.request.headers._dict:
                headers["site_deployment_id"] = session_info.ws.request.headers._dict["X-Site-Deployment-Id"]
        except Exception as ex:
            pass
        return headers

    def main(self):
        st.title('Azure Test Availability')
        if not st.session_state.http_headers["site_host"]:
            st.session_state.http_headers = self._get_session_http_headers()
        st.write("Web Host: ", st.session_state.http_headers["site_host"])
        st.dataframe(st.session_state["df_results"])  # Same as st.write(df)


    def _get_orders(self):
        with pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT TOP 10 OrderDate, SalesOrderNumber, PurchaseOrderNumber, CustomerID, TotalDue FROM SalesLT.SalesOrderHeader")
                row = cursor.fetchone()
                while row:
                    st.session_state.orders.append([str(row[0]), str(row[1]), str(row[2]), str(row[3]), str(row[4])])
                    row = cursor.fetchone()

if __name__ == "__main__":
    app = App()
    app.main()