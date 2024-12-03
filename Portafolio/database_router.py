#indica a Django qué base de datos utilizar para cada operación.


#si estamos en la app 'dashboard' utilizar la base de datos 'dashboar'
#definida en DATABASES de setting.py
class DashboardRouter:
    """
    Un router para leer/escribir datos del dashboard.
    """

    def db_for_read(self, model, **hints):
        """
        Dirige las consultas de lectura de modelos específicos a la base de datos del dashboard.
        """
        if model._meta.app_label == 'dashboard':
            return 'dashboard'
        return 'default'

    def db_for_write(self, model, **hints):
        """
        Dirige las consultas de escritura de modelos específicos a la base de datos del dashboard.
        """
        if model._meta.app_label == 'dashboard':
            return 'dashboard'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """
        Permite relaciones entre objetos en ambas bases de datos.
        """
        db_set = {'default', 'dashboard'}
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Asegura que las migraciones de ciertas aplicaciones solo ocurran en la base de datos correcta.
        """
        if app_label == 'dashboard':
            return db == 'dashboard'
        return db == 'default'