import slidingWindow as sw # para poder llamar así a la clase, guárdela en un archivo llamado slidingWindow.py

window_size = 3
initial_seq = 3
message = "Esta es una prueba de sliding window"
message_length = len(message.encode())

# mensaje "Esta es una prueba de sliding window." separado en grupos de 4 caracteres.
data_list = [message_length, "Esta", " es ", "una ", "prue", "ba", "e sl", "idin", "g wi", "ndow"]

# creamos un objeto SlidingWindow
data_window = sw.SlidingWindow(window_size, data_list, initial_seq)

# Podemos imprimir la ventana inicial
print(data_window)
# y nos muestra lo siguiente:
# +------+---------+---------+---------+
# | Data | 37      | Esta    |  es     |
# +------+---------+---------+---------+
# | Seq  | Y+0 = 3 | Y+1 = 4 | Y+2 = 5 |
# +------+---------+---------+---------+

# Avanzamos la ventana en 2 espacios y luego otros 3
data_window.move_window(2)
data_window.move_window(3)
print(data_window)

# si avanzamos lo suficiente la ventana se acaban los datos
data_window.move_window(1)
data_window.move_window(3)
if data_window.get_sequence_number(2) == None and data_window.get_data(2) == None:
    print("el último elemento de la ventana es igual a None")
    print(data_window) 
# También podemos crear ventanas vacías de la siguiente forma:
empty_window = sw.SlidingWindow(window_size, [], initial_seq)
print(empty_window)

# y podemos añadir datos a esta ventana
add_data = "Hola"
seq = initial_seq + 2
window_index = 2
empty_window.put_data(add_data, seq, window_index)
print(empty_window)