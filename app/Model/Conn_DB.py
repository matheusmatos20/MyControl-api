class Conn:
    def __init__(self):
        # self._str_conn = "DRIVER={SQL Server};SERVER=localhost;DATABASE=db_grantempo;Trusted_Connection=yes;"
        self._str_conn = (
            "DRIVER={SQL Server};"
            "SERVER=mfmatos_grantempo.sqlserver.dbaas.com.br;"
            "DATABASE=mfmatos_grantempo;"
            "UID=mfmatos_grantempo;"
            "PWD=gr@ntempo2024"
        )

    @property
    def str_conn(self):
        return self._str_conn 
