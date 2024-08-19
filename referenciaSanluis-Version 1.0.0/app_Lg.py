import tkinter as tk
import datetime
from tkinter import ttk, messagebox, PhotoImage, simpledialog
from database_Lg import create_connection, obtener_diagnosticos
from datetime import date, timedelta, datetime

# Conexion a la base de datos
conn = create_connection()


def insertar_datos():
    # Obtencion de los valores de los campos
    fecha_hora_turno = entry_turno.get()
    fecha_hora_llamado = entry_llamado.get()
    fecha_hora_aceptacion = entry_aceptacion.get() if entry_aceptacion.get() else None
    municipio_referencia = entry_municipio.get()
    entidad_remisora = entry_entidad.get()
    nombres_apellidos = entry_nombres.get()
    tipo_doc = combo_tipo_doc.get()
    documento = entry_documento.get()
    edad = entry_edad.get()
    asegurador = entry_asegurador.get()
    regimen = combo_regimen.get()
    diagnostico = entry_diagnostico.get()
    servicio = combo_servicio.get()
    causa_no_aceptacion = entry_causa.get()
    usuario_san_luis = entry_usuario.get()

    # Validación: todos los campos estan diligenciados, excepto fecha_hora_aceptacion y causa_no_aceptacion
    if not all([fecha_hora_turno, fecha_hora_llamado, municipio_referencia, entidad_remisora,
                nombres_apellidos, tipo_doc, documento, edad, asegurador, regimen, diagnostico, servicio,
                usuario_san_luis]):
        messagebox.showerror("Error", "Todos los campos deben ser completados, "
                                      "excepto: Fecha de Aceptación y Causa de no Aceptación")
        return

    # Verificación de documento existente
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM turnos WHERE documento = %s", (documento,))
    resultado = cursor.fetchone()[0]
    cursor.close()

    if resultado > 0:
        respuesta = messagebox.askyesno("Reingreso", "¿El paciente es un reingreso?")
        if not respuesta:
            return

    # Inserción de datos a la base de datos
    cursor = conn.cursor()
    sql = """INSERT INTO turnos (fecha_hora_turno, fecha_hora_llamado, fecha_hora_aceptacion, municipio_referencia,
     entidad_remisora, nombres_apellidos, tipo_doc, documento, edad, asegurador, regimen, diagnostico, servicio, 
     causa_no_aceptacion, usuario_san_luis) 
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    values = (fecha_hora_turno, fecha_hora_llamado, fecha_hora_aceptacion, municipio_referencia, entidad_remisora,
              nombres_apellidos, tipo_doc, documento, edad, asegurador, regimen, diagnostico, servicio,
              causa_no_aceptacion, usuario_san_luis)

    cursor.execute(sql, values)
    conn.commit()
    cursor.close()
    messagebox.showinfo("Información", "Datos insertados correctamente")
    limpiar_campos()
    mostrar_datos()


# Definición de funciones
def obtener_fecha_hora():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def establecer_fecha_hora(campo):
    campo.delete(0, tk.END)
    campo.insert(0, obtener_fecha_hora())


def mostrar_datos():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM turnos")
    records = cursor.fetchall()
    cursor.close()

    # Obtener la fecha de hoy y la fecha de ayer
    hoy = date.today()
    ayer = hoy - timedelta(days=1)

    # Filtrar los registros para mostrar solo los del día anterior y del día actual
    registros_filtrados = [record for record in records if record[1].date() in (ayer, hoy)]

    # Limpiar el visor y agregar los registros filtrados
    for row in visor.get_children():
        visor.delete(row)
    for record in registros_filtrados:
        visor.insert("", "end", values=record)


def actualizar_fecha_aceptacion():
    selected_item = visor.selection()
    if not selected_item:
        messagebox.showerror("Error", "Por favor, seleccione un registro")
        return

    item = visor.item(selected_item)
    record_id = item['values'][0]

    fecha_hora_aceptacion = obtener_fecha_hora()

    cursor = conn.cursor()
    sql = "UPDATE turnos SET fecha_hora_aceptacion = %s WHERE id = %s"
    cursor.execute(sql, (fecha_hora_aceptacion, record_id))
    conn.commit()
    cursor.close()

    messagebox.showinfo("Información", "Fecha de Aceptación actualizada correctamente")
    limpiar_campos()
    mostrar_datos()


def buscar_por_documento(entry):
    documento = entry.get()
    if not documento:
        messagebox.showerror("Error", "Por favor, ingrese un número de documento")
        return

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM turnos WHERE documento = %s", (documento,))
    records = cursor.fetchall()
    cursor.close()

    for row in visor.get_children():
        visor.delete(row)
    for record in records:
        visor.insert("", "end", values=record)


# Función para limpiar campos y volver a mostrar registros del día de hoy

def limpiar_campos_y_refrescar():
    limpiar_campos()
    mostrar_datos()


def limpiar_campos():
    entry_turno.delete(0, tk.END)
    entry_llamado.delete(0, tk.END)
    entry_aceptacion.delete(0, tk.END)
    entry_municipio.delete(0, tk.END)
    entry_entidad.delete(0, tk.END)
    entry_nombres.delete(0, tk.END)
    combo_tipo_doc.set("")
    entry_documento.delete(0, tk.END)
    entry_edad.delete(0, tk.END)
    entry_asegurador.delete(0, tk.END)
    combo_regimen.set("")
    entry_diagnostico.set("")
    combo_servicio.set("")
    entry_causa.delete(0, tk.END)
    entry_usuario.delete(0, tk.END)
    entry_buscar_documento.delete(0, tk.END)


def mostrar_menu_contextual(event):
    item_id = visor.identify_row(event.y)
    if item_id:
        visor.selection_set(item_id)
        menu.post(event.x_root, event.y_root)


def editar_registro():
    selected_item = visor.selection()
    if not selected_item:
        messagebox.showerror("Error", "Por favor, seleccione un registro")
        return

    item = visor.item(selected_item)
    record_id = item['values'][0]

    # Confirmar edición
    respuesta = messagebox.askyesno("Confirmación", "¿Desea editar este registro?")
    if not respuesta:
        return

    # Pedir motivo de la modificación
    motivo = simpledialog.askstring("Motivo de la Modificación", "Ingrese el motivo de la modificación:")
    if not motivo:
        messagebox.showwarning("Advertencia", "El motivo de la modificación es obligatorio.")
    usuario2 = simpledialog.askstring("Usuario San Luis", "Ingrese su usuario:")
    if not usuario2:
        messagebox.showwarning("Advertencia", "El usuario es obligatorio.")
        return

    # Cargar datos en el formulario para edición
    entry_turno.delete(0, tk.END)
    entry_turno.insert(0, item['values'][1])
    entry_llamado.delete(0, tk.END)
    entry_llamado.insert(0, item['values'][2])
    entry_aceptacion.delete(0, tk.END)
    entry_aceptacion.insert(0, item['values'][3])
    entry_municipio.delete(0, tk.END)
    entry_municipio.insert(0, item['values'][4])
    entry_entidad.delete(0, tk.END)
    entry_entidad.insert(0, item['values'][5])
    entry_nombres.delete(0, tk.END)
    entry_nombres.insert(0, item['values'][6])
    combo_tipo_doc.set(item['values'][7])
    entry_documento.delete(0, tk.END)
    entry_documento.insert(0, item['values'][8])
    entry_edad.delete(0, tk.END)
    entry_edad.insert(0, item['values'][9])
    entry_asegurador.delete(0, tk.END)
    entry_asegurador.insert(0, item['values'][10])
    combo_regimen.set(item['values'][11])
    entry_diagnostico.set(item['values'][12])
    combo_servicio.set(item['values'][13])
    entry_causa.delete(0, tk.END)
    entry_causa.insert(0, item['values'][14])
    entry_usuario.delete(0, tk.END)
    entry_usuario.insert(0, item['values'][15])  # Asegúrate de que el índice es correcto

    # Guardar cambios en el formulario
    def guardar_cambios():
        fecha_hora_turno = entry_turno.get()
        fecha_hora_llamado = entry_llamado.get()
        fecha_hora_aceptacion = entry_aceptacion.get() if entry_aceptacion.get() else None
        municipio_referencia = entry_municipio.get()
        entidad_remisora = entry_entidad.get()
        nombres_apellidos = entry_nombres.get()
        tipo_doc = combo_tipo_doc.get()
        documento = entry_documento.get()
        edad = entry_edad.get()
        asegurador = entry_asegurador.get()
        regimen = combo_regimen.get()
        diagnostico = entry_diagnostico.get()
        servicio = combo_servicio.get()
        causa_no_aceptacion = entry_causa.get()
        usuario_san_luis = entry_usuario.get()

        # Actualizar registro en la base de datos
        cursor = conn.cursor()
        sql = """UPDATE turnos SET fecha_hora_turno = %s, fecha_hora_llamado = %s, fecha_hora_aceptacion = %s,
                  municipio_referencia = %s, entidad_remisora = %s, nombres_apellidos = %s, tipo_doc = %s,
                  documento = %s, edad = %s, asegurador = %s, regimen = %s, diagnostico = %s, servicio = %s,
                  causa_no_aceptacion = %s, usuario_san_luis = %s WHERE id = %s"""
        values = (fecha_hora_turno, fecha_hora_llamado, fecha_hora_aceptacion, municipio_referencia,
                  entidad_remisora, nombres_apellidos, tipo_doc, documento, edad, asegurador, regimen,
                  diagnostico, servicio, causa_no_aceptacion, usuario_san_luis, record_id)

        cursor.execute(sql, values)
        conn.commit()
        cursor.close()

        # Guardar motivo de la modificación en la base de datos
        cursor = conn.cursor()
        sql = "INSERT INTO ediciones (id_turno, motivo, usuario2) VALUES (%s, %s, %s)"
        cursor.execute(sql, (record_id, motivo, usuario2))
        conn.commit()
        cursor.close()

        messagebox.showinfo("Información", "Registro editado correctamente")
        mostrar_datos()
        limpiar_campos()

    # Agregar botón para guardar cambios
    btn_guardar = ttk.Button(frame_botones, text="Guardar cambios", command=guardar_cambios)
    btn_guardar.grid(row=0, column=2, padx=5, pady=5)


# Crear la ventana principal
root = tk.Tk()
root.title("REFERENCIA Y CONTRAREFERENCIA CLINICA SAN LUIS")

# Estilos con ttk
style = ttk.Style()
style.configure("TLabel", font=("Arial", 12), background="alice blue")
style.configure("TEntry", font=("Arial", 12))
style.configure("TButton", font=("Arial", 12), background="DeepSkyBlue3")
style.configure("TFrame", background="alice blue")

# Crear un frame principal
main_frame = ttk.Frame(root, padding="10", style="TFrame")
main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Crear los frames para secciones

frame_turno = ttk.Frame(main_frame, padding="10")
frame_turno.grid(row=0, column=0, sticky=(tk.W, tk.E))

frame_info = ttk.Frame(main_frame, padding="10")
frame_info.grid(row=1, column=0, sticky=(tk.W, tk.E))

frame_botones = ttk.Frame(main_frame, padding="15")
frame_botones.grid(row=2, column=0, sticky=(tk.W, tk.E))

frame_visor = ttk.Frame(main_frame, padding="10")
frame_visor.grid(row=3, column=0, sticky=(tk.W, tk.E))

# Cargar y agregar el logo
#logo = PhotoImage(file="logosanluis.png")
#logo_label = tk.Label(frame_turno, image=logo)
#logo_label.grid(row=0, column=5, padx=1, pady=20)

# Frame para Fecha y Hora
ttk.Label(frame_turno, text="Fecha y Hora de Turno").grid(row=1, column=1, padx=5, pady=5)
entry_turno = ttk.Entry(frame_turno)
entry_turno.grid(row=1, column=2, padx=5, pady=5)
btn_turno = ttk.Button(frame_turno, text="Asignar", command=lambda: establecer_fecha_hora(entry_turno))
btn_turno.grid(row=1, column=3, padx=5, pady=5)

ttk.Label(frame_turno, text="Fecha y Hora de Llamado").grid(row=1, column=4, padx=5, pady=5)
entry_llamado = ttk.Entry(frame_turno)
entry_llamado.grid(row=1, column=5, padx=5, pady=5)
btn_llamado = ttk.Button(frame_turno, text="Asignar", command=lambda: establecer_fecha_hora(entry_llamado))
btn_llamado.grid(row=1, column=6, padx=5, pady=5)

ttk.Label(frame_turno, text="Fecha y Hora de Aceptación").grid(row=1, column=7, padx=5, pady=5)
entry_aceptacion = ttk.Entry(frame_turno)
entry_aceptacion.grid(row=1, column=8, padx=5, pady=5)
btn_aceptacion = ttk.Button(frame_turno, text="Asignar", command=lambda: establecer_fecha_hora(entry_aceptacion))
btn_aceptacion.grid(row=1, column=9, padx=5, pady=5)

# Frame para Información del Paciente
ttk.Label(frame_info, text="Municipio de Referencia").grid(row=0, column=0, padx=5, pady=5)
entry_municipio = ttk.Entry(frame_info)
entry_municipio.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(frame_info, text="Entidad Remisora").grid(row=0, column=2, padx=5, pady=5)
entry_entidad = ttk.Entry(frame_info)
entry_entidad.grid(row=0, column=3, padx=5, pady=5)

ttk.Label(frame_info, text="Nombres y Apellidos").grid(row=0, column=4, padx=5, pady=5)
entry_nombres = ttk.Entry(frame_info)
entry_nombres.grid(row=0, column=5, padx=5, pady=5)

ttk.Label(frame_info, text="Documento").grid(row=0, column=6, padx=5, pady=5)
entry_documento = ttk.Entry(frame_info)
entry_documento.grid(row=0, column=7, padx=5, pady=5)

ttk.Label(frame_info, text="Tipo de Documento").grid(row=1, column=0, padx=5, pady=5)
combo_tipo_doc = ttk.Combobox(frame_info, values=["CC", "TI", "RC", "CE", "Otro"], state='readonly')
combo_tipo_doc.grid(row=1, column=1, padx=5, pady=5)

ttk.Label(frame_info, text="Edad").grid(row=1, column=2, padx=5, pady=5)
entry_edad = ttk.Entry(frame_info)
entry_edad.grid(row=1, column=3, padx=5, pady=5)

ttk.Label(frame_info, text="Asegurador").grid(row=1, column=4, padx=5, pady=5)
entry_asegurador = ttk.Entry(frame_info)
entry_asegurador.grid(row=1, column=5, padx=5, pady=5)

ttk.Label(frame_info, text="Régimen").grid(row=1, column=6, padx=5, pady=5)
combo_regimen = ttk.Combobox(frame_info, values=["Contributivo", "Subsidiado", "Especial", "Otro"], state='readonly')
combo_regimen.grid(row=1, column=7, padx=5, pady=5)

ttk.Label(frame_info, text="Diagnóstico").grid(row=3, column=0, padx=5, pady=5)
entry_diagnostico = ttk.Combobox(frame_info, state='write')
entry_diagnostico.grid(row=3, column=1, padx=5, pady=5)

ttk.Label(frame_info, text="Servicio").grid(row=3, column=2, padx=5, pady=5)
combo_servicio = ttk.Combobox(frame_info,
                              values=["Urgencias", "Hospitalización", "Cirugía", "Consulta Externa", "Otro"],
                              state='readonly')
combo_servicio.grid(row=3, column=3, padx=5, pady=5)

ttk.Label(frame_info, text="Causa de No Aceptación").grid(row=3, column=4, padx=5, pady=5)
entry_causa = ttk.Entry(frame_info)
entry_causa.grid(row=3, column=5, padx=5, pady=5)

ttk.Label(frame_info, text="Usuario San Luis").grid(row=3, column=6, padx=5, pady=5)
entry_usuario = ttk.Entry(frame_info)
entry_usuario.grid(row=3, column=7, padx=5, pady=5)


# Función de autocompletado
def autocompletar(event):
    value = entry_diagnostico.get()
    if value == '':
        entry_diagnostico['values'] = diagnosticos
    else:
        data = []
        for item in diagnosticos:
            if value.lower() in item.lower():
                data.append(item)
        entry_diagnostico['values'] = data


diagnosticos = obtener_diagnosticos()
entry_diagnostico.bind('<KeyRelease>', autocompletar)

# Botón para enviar el formulario
ttk.Button(frame_botones, text="Enviar", command=insertar_datos).grid(row=0, column=0, padx=5, pady=5)

# Botón para actualizar la fecha de aceptación
ttk.Button(frame_botones, text="Actualizar Fecha de Aceptación", command=actualizar_fecha_aceptacion).grid(row=0,
                                                                                                           column=1,
                                                                                                           padx=5,
                                                                                                           pady=5)

ttk.Label(frame_botones, text="Buscar por Documento").grid(row=0, column=3, padx=5, pady=5)
entry_buscar_documento = ttk.Entry(frame_botones)
entry_buscar_documento.grid(row=0, column=4, padx=5, pady=5)
btn_buscar_documento = ttk.Button(frame_botones, text="Buscar",
                                  command=lambda: buscar_por_documento(entry_buscar_documento))
btn_buscar_documento.grid(row=0, column=5, padx=5, pady=5)

# Agregar botón para limpiar campos y volver a mostrar registros del día de hoy

ttk.Button(frame_botones, text="Limpiar y Refrescar", command=limpiar_campos_y_refrescar).grid(row=0, column=6, padx=5,
                                                                                               pady=5)

# Visor de datos
columnas = ("ID", "Fecha y Hora de Turno", "Fecha y Hora de Llamado", "Fecha y Hora de Aceptación",
            "Municipio de Referencia", "Entidad Remisora", "Nombres y Apellidos", "Tipo de Documento",
            "Documento", "Edad", "Asegurador", "Régimen", "Diagnóstico", "Servicio",
            "Causa de No Aceptación", "Usuario San Luis")

visor = ttk.Treeview(frame_visor, columns=columnas, show='headings')

for columna in columnas:
    visor.heading(columna, text=columna)
    visor.column(columna, width=90)

visor.grid(row=0, column=0, sticky='nsew')
scrollbar = ttk.Scrollbar(frame_visor, orient=tk.VERTICAL, command=visor.yview)
visor.configure(yscroll=scrollbar.set)
scrollbar.grid(row=0, column=1, sticky='ns')

# Agregar menú contextual
menu = tk.Menu(root, tearoff=0)
menu.add_command(label="Editar", command=editar_registro)

visor.bind("<Button-3>", mostrar_menu_contextual)

# Mostrar los datos al iniciar la aplicación
mostrar_datos()

root.mainloop()
