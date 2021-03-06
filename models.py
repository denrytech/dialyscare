import datetime

from flask import Flask
from flask_login import UserMixin
from flask_bcrypt import generate_password_hash
from peewee import *

import config

# Print all queries to stderr.
# import logging
# logger = logging.getLogger('peewee')
# logger.addHandler(logging.StreamHandler())
# logger.setLevel(logging.DEBUG)


db = MySQLDatabase(config.DB_NAME, # nombre de la base de datos
                   host=config.DB_HOST,
                   user=config.DB_USER,
                   password=config.DB_PASSWORD,
                   port=config.DB_PORT)


class MyModel(Model):  # Con esta clase ya establezco la base de datos que van a usar todos los modelos
    class Meta:
        database = db


class General(MyModel):
    admin_nombre = CharField(max_length=60)
    admin_email = CharField(max_length=60)
    admin_telefono = CharField(max_length=20)
    balanza_clave = IntegerField()

    class Meta:
        table_name = 'general'
        primary_key = False

    @classmethod
    def default_data(cls):
        """Agregar datos por defecto"""
        data_source = {'admin_nombre': 'Denry Techera',
                'admin_email': 'denrytech@gmail.com',
                'admin_telefono': '091243955',
                'balanza_clave': 918273}

        cls.create(**data_source)


class Personas(MyModel):
    id = PrimaryKeyField()
    nombres = CharField(max_length=45)
    apellidos = CharField(max_length=45)
    email = CharField(max_length=255, unique=True)
    ci = IntegerField(unique=True)
    telefono1 = CharField(20)
    telefono2 = CharField(null=True, max_length=20)
    telefono3 = CharField(null=True, max_length=20)
    direccion = TextField()
    localidad = CharField(40)
    departamento = CharField(40)
    pais = CharField(40)
    fecha_de_nacimiento = DateField()
    sexo = FixedCharField(max_length=1)
    ingreso = DateTimeField(default=datetime.datetime.now())
    #ingreso = TimestampField(default=int(datetime.datetime.now().timestamp()))   otra forma de hacerlo
    observaciones = TextField(null = True)
    estado = BooleanField()

    class Meta:
        table_name = 'personas'

    @classmethod
    def create_persona(cls, nombres, apellidos, email, ci, telefono1, telefono2,
                        telefono3, direccion, localidad, departamento,
                        pais, fecha_de_nacimiento, sexo, observaciones = '',
                        estado = True):
        try:
            persona = cls.create(
                nombres = nombres,
                apellidos = apellidos,
                email = email,
                ci = ci,
                telefono1 = telefono1,
                telefono2 = telefono2,
                telefono3 = telefono3,
                direccion = direccion,
                localidad = localidad,
                departamento = departamento,
                pais = pais,
                fecha_de_nacimiento = fecha_de_nacimiento,
                sexo = sexo,
                observaciones = observaciones,
                estado = estado
            )

            return persona
        except IntegrityError:
            raise ValueError('La persona ya existe')


class Usuarios(UserMixin, MyModel):
    id = PrimaryKeyField()
    persona = ForeignKeyField(Personas, backref='usuario', unique=True)
    rol = CharField(max_length=20)
    usuario = CharField(max_length=20, unique=True)
    clave = CharField(66)

    class Meta:
        table_name = 'usuarios'

    @classmethod
    def create_usuario(cls, p_nombres, p_apellidos, p_email, p_ci, p_telefono1,
        p_telefono2, p_telefono3, p_direccion, p_localidad, p_departamento, p_pais,
        p_fecha_de_nacimiento, p_sexo, p_observaciones, p_estado, u_rol, u_usuario,
        u_clave):

        try:
            persona = Personas.create_persona(p_nombres, p_apellidos, p_email,
                p_ci, p_telefono1, p_telefono2, p_telefono3, p_direccion, p_localidad,
                p_departamento, p_pais, p_fecha_de_nacimiento, p_sexo, p_observaciones,
                p_estado)

            usuario = cls.create(
                persona = persona,
                rol = u_rol,
                usuario = u_usuario,
                clave = generate_password_hash(u_clave)
            )
            return usuario

        except IntegrityError:
            raise ValueError('El usuario ya existe')

    @classmethod
    def check_email(cls, email):
        try:
            persona = Personas.get(Personas.email == email)
        except:
            return False
        else:
            return True

    @classmethod
    def check_ci(cls, ci):
        try:
            persona = Personas.get(Personas.ci == ci)
            print(persona)
        except:
            return False
        else:
            return True

    @classmethod
    def list( cls ):
        query = cls.select().join(Personas).order_by(Personas.apellidos)
        return query

    @classmethod
    def update_usuario(cls, id, p_nombres, p_apellidos, p_email, p_ci, p_telefono1,
        p_telefono2, p_telefono3, p_direccion, p_localidad, p_departamento, p_pais,
        p_fecha_de_nacimiento, p_sexo, p_observaciones, p_estado, u_rol, u_usuario, u_clave
        ):

        try:
            usuario = cls.get_by_id(id)
            usuario.rol = u_rol
            usuario.clave = u_clave
            usuario.usuario=u_usuario
            usuario.save()

            persona = Personas.get_by_id(usuario.persona.id)
            persona.nombres = p_nombres
            persona.apellidos = p_apellidos
            persona.email = p_email
            persona.ci = p_ci
            persona.telefono1 = p_telefono1
            persona.telefono2 = p_telefono2
            persona.telefono3 = p_telefono3
            persona.direccion = p_direccion
            persona.localidad = p_localidad
            persona.departamento = p_departamento
            persona.pais = p_pais
            persona.fecha_de_nacimiento = p_fecha_de_nacimiento
            persona.sexo = p_sexo
            persona.observaciones = p_observaciones
            persona.estado = p_estado
            persona.save()

            return usuario

        except IntegrityError as e:
            raise ValueError('Error de integridad al intentar editar datos del paciente')


class Doctores(MyModel):
    id = PrimaryKeyField()
    usuario = ForeignKeyField(Usuarios, backref='doctor', unique=True)
    numero_profesional = IntegerField(unique=True)
    super_doctor = BooleanField(default=False)

    class Meta:
        table_name = 'doctores'

    @classmethod
    def create_doctor(cls, p_nombres, p_apellidos, p_email, p_ci, p_telefono1,
        p_telefono2, p_telefono3, p_direccion, p_localidad, p_departamento, p_pais,
        p_fecha_de_nacimiento, p_sexo, p_observaciones, p_estado, u_usuario,
        u_clave, super_doctor, numero_profesional):
        try:
            usuario = Usuarios.create_usuario(p_nombres, p_apellidos, p_email, p_ci, p_telefono1,
                p_telefono2, p_telefono3, p_direccion, p_localidad, p_departamento, p_pais,
                p_fecha_de_nacimiento, p_sexo, p_observaciones, p_estado, 'doctor', u_usuario,
                u_clave)

            doctor = cls.create(
                usuario = usuario,
                numero_profesional = numero_profesional,
                super_doctor = super_doctor
            )

            return doctor
        except IntegrityError:
            raise ValueError('El doctor ya existe o hay algun otro problema')

    @classmethod
    def list( cls ):
        return cls.select()


class Nurses(MyModel):
    id = PrimaryKeyField()
    usuario = ForeignKeyField(Usuarios, backref='nurse')
    super_nurse = BooleanField(default=False)

    class Meta:
        table_name = 'nurses'

    @classmethod
    def create_nurse(cls, p_nombres, p_apellidos, p_email, p_ci, p_telefono1,
        p_telefono2, p_telefono3, p_direccion, p_localidad, p_departamento, p_pais,
        p_fecha_de_nacimiento, p_sexo, p_observaciones, p_estado, u_usuario,
        u_clave, super_nurse = False):
        try:
            usuario = Usuarios.create_usuario(p_nombres, p_apellidos, p_email, p_ci, p_telefono1,
                p_telefono2, p_telefono3, p_direccion, p_localidad, p_departamento, p_pais,
                p_fecha_de_nacimiento, p_sexo, p_observaciones, p_estado, 'nurse', u_usuario,
                u_clave)

            nurse = cls.create(
                usuario = usuario,
                super_nurse = super_nurse
            )

            return nurse
        except IntegrityError:
            raise ValueError('El nurse ya existe')

    @classmethod
    def list( cls ):
        return cls.select()


class Enfermeros(MyModel):
    id = PrimaryKeyField()
    usuario = ForeignKeyField(Usuarios, backref='enfermero', unique=True)

    class Meta:
        table_name = 'enfermeros'

    @classmethod
    def create_enfermero(cls, p_nombres, p_apellidos, p_email, p_ci, p_telefono1,
        p_telefono2, p_telefono3, p_direccion, p_localidad, p_departamento, p_pais,
        p_fecha_de_nacimiento, p_sexo, p_observaciones, p_estado, u_usuario,
        u_clave):
        try:
            usuario = Usuarios.create_usuario(p_nombres, p_apellidos, p_email, p_ci, p_telefono1,
                p_telefono2, p_telefono3, p_direccion, p_localidad, p_departamento, p_pais,
                p_fecha_de_nacimiento, p_sexo, p_observaciones, p_estado, 'enfermero', u_usuario,
                u_clave)

            enfermero = cls.create(
                usuario = usuario
            )

            return enfermero
        except IntegrityError:
            raise ValueError('El enfermero ya existe')

    @classmethod
    def list( cls ):
        return cls.select()


class Administrativos(MyModel):
    id = PrimaryKeyField()
    usuario = ForeignKeyField(Usuarios, backref='administrativo')

    class Meta:
        table_name = 'administrativos'

    @classmethod
    def create_administrativo(cls, p_nombres, p_apellidos, p_email, p_ci, p_telefono1,
        p_telefono2, p_telefono3, p_direccion, p_localidad, p_departamento, p_pais,
        p_fecha_de_nacimiento, p_sexo, p_observaciones, p_estado, u_usuario,
        u_clave):
        try:
            usuario = Usuarios.create_usuario(p_nombres, p_apellidos, p_email, p_ci, p_telefono1,
                p_telefono2, p_telefono3, p_direccion, p_localidad, p_departamento, p_pais,
                p_fecha_de_nacimiento, p_sexo, p_observaciones, p_estado, 'administrativo', u_usuario,
                u_clave)

            administrativo = cls.create(
                usuario = usuario
            )

            return administrativo
        except IntegrityError:
            raise ValueError('El administrativo ya existe')

    @classmethod
    def list( cls ):
        return cls.select()


class Mutualistas(MyModel):
    id = PrimaryKeyField()
    nombre = CharField(max_length=45)

    class Meta:
        table_name = 'mutualistas'

    @classmethod
    def check_mutualista_exists(cls, nombre):
        try:
            mutualista = cls.get(cls.nombre == nombre)
        except:
            return False
        else:
            return True

    @classmethod
    def list( cls ):
        return cls.select()


class Pacientes(MyModel):
    id = PrimaryKeyField()
    persona = ForeignKeyField(Personas, backref='paciente', unique=True)
    mutualista = ForeignKeyField(Mutualistas, backref='paciente')
    doctor = ForeignKeyField(Doctores, backref='paciente')
    enfermero = ForeignKeyField(Enfermeros, backref='paciente')
    altura = IntegerField()
    tipo_de_paciente = CharField(max_length=20)
    tipo_de_acceso_vascular = CharField(max_length=20)
    grupo_sanguineo = CharField(max_length=2) # (A,B,AB,O)
    rh = FixedCharField(max_length=1) # Positivo='+' Negativo = '-' o rh = FixedCharField(max_length=8)
    primer_dialisis = DateField('%d,%m,%Y')
    diabetico = BooleanField(default=False)
    hta = BooleanField(default=False)
    alergico = BooleanField(default=False)
    numero_fnr = IntegerField()
    habilitar_lavado_capilar = BooleanField()
    tipo_de_puesto = CharField(max_length=20)

    class Meta:
        table_name = 'pacientes'

    @classmethod
    def create_paciente(cls, p_nombres, p_apellidos, p_email, p_ci, p_telefono1,
        p_telefono2, p_telefono3, p_direccion, p_localidad, p_departamento, p_pais,
        p_fecha_de_nacimiento, p_sexo, p_observaciones, p_estado, mutualista,
        doctor, enfermero, altura, tipo_de_paciente, tipo_de_acceso_vascular,
        grupo_sanguineo, rh, primer_dialisis, diabetico, hta, alergico, numero_fnr,
        habilitar_lavado_capilar, tipo_de_puesto):

        try:
            persona = Personas.create_persona(p_nombres, p_apellidos, p_email,
                p_ci, p_telefono1, p_telefono2, p_telefono3, p_direccion, p_localidad,
                p_departamento, p_pais, p_fecha_de_nacimiento, p_sexo, p_observaciones,
                p_estado)

            paciente = cls.create(
                persona = persona,
                mutualista = mutualista,
                doctor = doctor,
                enfermero = enfermero,
                altura = altura,
                tipo_de_paciente = tipo_de_paciente,
                tipo_de_acceso_vascular = tipo_de_acceso_vascular,
                grupo_sanguineo = grupo_sanguineo,
                rh = rh,
                primer_dialisis = primer_dialisis,
                diabetico = diabetico,
                hta = hta,
                alergico = alergico,
                numero_fnr = numero_fnr,
                habilitar_lavado_capilar = habilitar_lavado_capilar,
                tipo_de_puesto = tipo_de_puesto
            )

            return paciente

        except IntegrityError as e:
            raise ValueError('El paciente ya existe')

    @classmethod
    def update_paciente(cls, id, p_nombres, p_apellidos, p_email, p_ci, p_telefono1,
        p_telefono2, p_telefono3, p_direccion, p_localidad, p_departamento, p_pais,
        p_fecha_de_nacimiento, p_sexo, p_observaciones, p_estado, mutualista,
        doctor, enfermero, altura, tipo_de_paciente, tipo_de_acceso_vascular,
        grupo_sanguineo, rh, primer_dialisis, diabetico, hta, alergico, numero_fnr,
        habilitar_lavado_capilar, tipo_de_puesto):

        try:
            paciente = cls.get_by_id(id)
            paciente.mutualista = mutualista
            paciente.doctor = doctor
            paciente.enfermero = enfermero
            paciente.altura = altura
            paciente.tipo_de_paciente = tipo_de_paciente
            paciente.tipo_de_acceso_vascular = tipo_de_acceso_vascular
            paciente.grupo_sanguineo = grupo_sanguineo
            paciente.rh = rh
            paciente.primer_dialisis = primer_dialisis
            paciente.diabetico = diabetico
            paciente.hta = hta
            paciente.alergico = alergico
            paciente.numero_fnr = numero_fnr
            paciente.habilitar_lavado_capilar = habilitar_lavado_capilar
            paciente.tipo_de_puesto = tipo_de_puesto
            paciente.save()

            persona = Personas.get_by_id(paciente.persona.id)
            persona.nombres = p_nombres
            persona.apellidos = p_apellidos
            persona.email = p_email
            persona.ci = p_ci
            persona.telefono1 = p_telefono1
            persona.telefono2 = p_telefono2
            persona.telefono3 = p_telefono3
            persona.direccion = p_direccion
            persona.localidad = p_localidad
            persona.departamento = p_departamento
            persona.pais = p_pais
            persona.fecha_de_nacimiento = p_fecha_de_nacimiento
            persona.sexo = p_sexo
            persona.observaciones = p_observaciones
            persona.estado = p_estado
            persona.save()

            return paciente

        except IntegrityError as e:
            raise ValueError('Error de integridad al intentar editar datos del paciente')

    @classmethod
    def check_email(cls, email):
        try:
            persona = Personas.get(Personas.email == email)
        except:
            return False
        else:
            return True

    @classmethod
    def check_ci(cls, ci):
        try:
            persona = Personas.get(Personas.ci == ci)
        except:
            return False
        else:
            return True

    @classmethod
    def list( cls ):
        query = cls.select().join(Personas).order_by(Personas.nombres)
        return query


class Indicaciones(MyModel):
    id = PrimaryKeyField()
    paciente = ForeignKeyField(Pacientes, backref='indicaciones')
    doctor = ForeignKeyField(Doctores, backref='indicaciones')
    anio = DateField('%Y')
    mes = DateField('%m')
    horas = TimeField('%H,%M')
    peso_seco = IntegerField()
    flujo_de_bomba = IntegerField()
    flujo_de_banio = IntegerField()
    bicarbonato = IntegerField()
    heparina_hbpm = IntegerField()
    lavados = CharField(max_length=45)
    tipo_de_capilar = CharField(max_length=20)
    epo_semanal = IntegerField()
    epo_sesion1 = IntegerField()
    epo_sesion2 = IntegerField()
    epo_sesion3 = IntegerField()
    hierro = CharField(max_length=45)
    sodio = IntegerField()
    medicacion_post_hd = TextField()
    vacunas = TextField()
    examenes_de_laboratorio = TextField()
    observaciones = TextField()

    class Meta:
        table_name = 'indicaciones'


class CoordinacionDeEstudios(MyModel):
    id = PrimaryKeyField()
    paciente = ForeignKeyField(Pacientes, backref= 'coordinacion_de_estudios')
    usuario = ForeignKeyField(Usuarios, backref= 'coordinacion_de_estudios')
    estudios = TextField()
    estado = BooleanField()

    class Meta:
        table_name = 'coordinacion_de_estudios'


class PedidosDeCambios(MyModel):
    id = PrimaryKeyField()
    paciente = ForeignKeyField(Pacientes, backref= 'pedidos_de_cambios')
    usuario = ForeignKeyField(Usuarios, backref= 'pedidos_de_cambios')
    pedido = TextField()
    estado = BooleanField()

    class Meta:
        table_name = 'pedidos_de_cambios'


class Salas(MyModel):
    id = PrimaryKeyField()
    nombre = CharField(max_length=45)

    class Meta:
        table_name = 'salas'


class Puestos(MyModel):
    id = PrimaryKeyField()
    sala = ForeignKeyField(Salas, backref= 'puestos')
    puesto_especial = BooleanField()
    tipo_de_puesto = CharField(max_length=20)

    class Meta:
        table_name = 'puestos'


class Agenda(MyModel):
    fecha = DateField('%d,%m,%Y')
    turno = FixedCharField(max_length=1)
    paciente = ForeignKeyField(Pacientes, backref= 'agenda')
    puesto = ForeignKeyField(Puestos, backref= 'agenda')
    peso_de_ingreso = IntegerField()
    peso_de_salida = IntegerField()
    falta = BooleanField()

    class Meta:
        primary_key = CompositeKey('fecha', 'turno', 'paciente')
        table_name = 'agenda'


class Sesiones(MyModel):
    id = PrimaryKeyField()
    paciente = ForeignKeyField(Pacientes, backref='sesiones')
    puesto = ForeignKeyField(Puestos, backref='sesiones')
    enfermero = ForeignKeyField(Enfermeros, backref='sesiones')
    doctor = ForeignKeyField(Doctores, backref='sesiones')
    nurse = ForeignKeyField(Nurses, backref='sesiones')
    fecha = DateField('%d,%m,%Y')
    turno = FixedCharField(max_length=1)
    dosis_de_anticoagulante = IntegerField()
    peso = IntegerField()
    peso_seco = IntegerField()
    ufc = IntegerField()
    tipo_de_acceso_vascular = CharField(max_length=20)
    dializado = CharField(max_length=20)
    minutos = IntegerField()
    medicacion = TextField()
    epo = BooleanField()
    hierro = BooleanField()
    hora_de_desconexión = TimeField()
    ktv = FloatField()
    presion_pre_a = IntegerField()
    presion_pre_b = IntegerField()
    presion_post_a = IntegerField()
    presion_post_b = IntegerField()
    temperatura = FloatField()
    flujo_de_banio = CharField(max_length=45)
    pre_conexion_paciente = BooleanField()
    pre_conexion_puesto = BooleanField()
    pre_conexion_capilar = BooleanField()
    post_conexion_lineas = BooleanField()
    post_conexion_bomba = BooleanField()
    post_conexion_uf = BooleanField()
    post_conexion_capilar = BooleanField()
    post_conexion_heparina = BooleanField()
    post_conexion_aire = BooleanField()
    equipo = IntegerField()
    hierrodesinfeccionialisis_extra = BooleanField()
    dialisis_extra_motivo = TextField()
    paraclinica_intradialisis = TextField()
    enviada_a_fnr = BooleanField()

    class Meta:
        table_name = 'sesiones'


class Recirculacion(MyModel):
    id = PrimaryKeyField()
    enfermero = ForeignKeyField(Enfermeros, backref= 'recirculacion')
    sesion = ForeignKeyField(Sesiones, backref= 'recirculacion')
    cualitest = BooleanField()
    cuantitest = BooleanField()

    class Meta:
        table_name = 'recirculacion'


class Controles(MyModel):
    id = PrimaryKeyField()
    enfermero = ForeignKeyField(Enfermeros, backref= 'controles')
    sesion = ForeignKeyField(Sesiones, backref= 'controles')
    hora = TimeField()
    flujo_de_bomba = IntegerField()
    pv = IntegerField()
    tmp = IntegerField()
    flujo_de_banio = IntegerField()
    conductividad = IntegerField()
    presion_arterial_a = IntegerField()
    presion_arterial_b = IntegerField()
    frecuencia_cardiaca = IntegerField()

    class Meta:
        table_name = 'controles'


class Capilares(MyModel):
    id = PrimaryKeyField()
    paciente = ForeignKeyField(Pacientes, backref= 'capilares')
    tipo_de_capilar = CharField(max_length=45)
    estado = BooleanField()

    class Meta:
        table_name = 'capilares'


class CapilaresAcciones(MyModel):
    id = PrimaryKeyField()
    capilar = ForeignKeyField(Capilares, backref= 'capilares_acciones')
    enfermero = ForeignKeyField(Enfermeros, backref= 'capilares_acciones')
    accion = CharField(max_length=45)
    fecha_hora = DateTimeField()
    volumen_min = IntegerField()
    volumen_residual = IntegerField()

    class Meta:
        table_name = 'capilares_acciones'


class CapilaresRecirculaciones(MyModel):
    capilar = ForeignKeyField(Capilares, backref= 'capilares_recirculaciones')
    recirculacion = ForeignKeyField(Recirculacion, backref= 'capilares_recirculaciones')

    class Meta:
        primary_key = CompositeKey('capilar', 'recirculacion')
        table_name = 'capilares_recirculaciones'


def initialize():
    db.connect()
    db.create_tables([General, Personas, Usuarios, Mutualistas, Doctores, Nurses,
        Enfermeros, Administrativos, Pacientes, Indicaciones, CoordinacionDeEstudios,
        PedidosDeCambios, Salas, Puestos, Agenda, Sesiones, Recirculacion, Controles,
        Capilares, CapilaresAcciones, CapilaresRecirculaciones], safe=True)
    db.close()



if __name__ == '__main__':
    db.connect()
    db.create_tables([General, Personas, Usuarios, Mutualistas, Doctores, Nurses,
        Enfermeros, Administrativos, Pacientes, Indicaciones, CoordinacionDeEstudios,
        PedidosDeCambios, Salas, Puestos, Agenda, Sesiones, Recirculacion, Controles,
        Capilares, CapilaresAcciones, CapilaresRecirculaciones], safe=True)
    # con safe=True no tira error si la tabla ya fue creada

    #Si no existe configuracion general, agregamos la por defecto
    if( General.select().count() == 0 ):
        General.default_data()

    ##Insertar datos de ejemplo

    ##Crear nurse en jefe
    if( Usuarios.check_ci(1234560) ):
        print('Horacio Sosa ya existe')
    else:
        nurse = Nurses.create_nurse(
            'Horacio',
            'Sosa',
            'horaciososa1@comero.com.uy',
            1234560,
            '091111111',
            'sin 2º telefono',
            'sin 3er telefono',
            'Ituzaingó 1234',
            'Rocha',
            'Rocha',
            'Uruguay',
            datetime.datetime.strptime('Jun 1 1965', '%b %d %Y'),
            'm',
            'Sin observaciones',
            True,
            'horaciososa',
            '123458',
            True
        )

        print('Horacio Sosa fue agregado con éxito')

    ##Crear doctora en jefe
    if( Usuarios.check_ci(2345678) ):
        doctor = Usuarios.get(Usuarios.usuario == 'deliapereyra').doctor
        print('Delia Pereyra ya existe')
    else:
        doctor = Doctores.create_doctor(
            'Delia',
            'Pereyra',
            'deliapereyra@comero.com.uy',
            2345678,
            '092222222',
            'sin 2º telefono',
            'sin 3er telefono',
            'General Artigas 1234',
            'Rocha',
            'Rocha',
            'Uruguay',
            datetime.datetime.strptime('Nov 3 1955', '%b %d %Y'),
            'f',
            'Sin observaciones',
            True,
            'deliapereyra',
            '654321',
            True,
            1234
        )

        print('Delia Pereyra fue agregada con éxito')

    ##Crear enfermera
    if( Usuarios.check_ci(3456789) ):
        enfermero = Usuarios.get(Usuarios.usuario == 'bettinarey').enfermero
        print('Bettina Rey ya existe')
    else:
        enfermero = Enfermeros.create_enfermero(
            'Bettina',
            'Rey',
            'bettinarey@comero.com.uy',
            3456789,
            '093333333',
            'sin 2º telefono',
            'sin 3er telefono',
            'Martinez Rodriguez 1234',
            'Rocha',
            'Rocha',
            'Uruguay',
            datetime.datetime.strptime('Jan 3 1945', '%b %d %Y'),
            'f',
            'Sin observaciones',
            True,
            'bettinarey',
            '123456'
        )

        print('Bettina Rey fue agregada con éxito')

    ##Crear mutualistas
    if( Mutualistas.check_mutualista_exists('ASSE') is False ):
        mutualista = Mutualistas.create(nombre = 'ASSE')
    else:
        mutualista = Mutualistas.get(Mutualistas.nombre == 'ASSE')

    if( Mutualistas.check_mutualista_exists('COMERO') is False ):
        Mutualistas.create(nombre = 'COMERO')

    if( Mutualistas.check_mutualista_exists('Médica Uruguaya') is False ):
        Mutualistas.create(nombre = 'Médica Uruguaya')

    ##Crear paciente
    if( Pacientes.check_ci(46944361) ):
        print('Denry Techera ya existe')
    else:
        paciente = Pacientes.create_paciente(
            'Denry',
            'Techera',
            'denrytech@gmail.com',
            46944361,
            '091243955',
            'sin 2º telefono',
            'sin 3er telefono',
            'Eliseo Marzol 1234',
            'Rocha',
            'Rocha',
            'Uruguay',
            datetime.datetime.strptime('Feb 9 1985', '%b %d %Y'),
            'm',
            'Sin observaciones',
            True,
            mutualista,
            doctor,
            enfermero,
            182,
            'ambulatorio',
            'fistula_nativa',
            'b',
            '+',
            datetime.datetime.strptime('Jul 9 2008', '%b %d %Y'),
            False,
            True,
            True,
            211076,
            True,
            'normal'
        )

        print('Denry Techera fue agregado con éxito')

    db.close()
