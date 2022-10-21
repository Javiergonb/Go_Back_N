class SlidingWindow:
    """Esta clase le permite crear ventanas deslizantes.
    Puede crear una ventana vacía con:
    SlidingWindow(window_size, [], initial_seq)."""

    def __init__(self, window_size, data_list, initial_seq):
        """Construye una ventana de tamaño window_size, usando los datos de
        data_list y número de secuencia inicial initial_seq (Y = initial_seq)."""

        if not isinstance(window_size, int):
            raise Exception("ERROR in SlidingWindow, __init___(): Index window_size must be an Integer")
        if not isinstance(initial_seq, int):
            raise Exception("ERROR in SlidingWindow, __init___(): Index initial_seq must be an Integer")
        if not isinstance(data_list, list):
            raise Exception("ERROR in SlidingWindow, __init___(): Index data_list must be a List")
        if window_size < 1:
            raise Exception("ERROR in SlidingWindow, __init___(): window_size must be > 0")
        if initial_seq < 0:
            raise Exception("ERROR in SlidingWindow, __init___(): initial_seq must be > 0")

        self.window_size = window_size
        self.data_list = data_list
        self.initial_seq = initial_seq

        self.possible_sequence_numbers = []
        for i in range(2 * self.window_size):
            self.possible_sequence_numbers.append(self.initial_seq + i)

        self.window = []
        i = 0
        for i in range(self.window_size):
            if i >= len(self.data_list):
                self.window.append({"data": None, "seq": None})
            else:
                self.window.append({"data": self.data_list[i],
                                    "seq": self.possible_sequence_numbers[i % (2 * self.window_size)]})
        self.data_start_index = i + 1

    def move_window(self, steps_to_move):
        """Avanza la ventana en steps_to_move espacios y actualiza los números de
        secuencia según corresponda. No puede avanzar más espacios que el tamaño
        de la ventana. Si se acaban los datos en data_list rellena con None."""

        if steps_to_move == 0:
            return
        if steps_to_move > self.window_size or steps_to_move < 0:
            raise Exception("ERROR in SlidingWindow, move_window(): Invalid index steps_to_move")
        if not isinstance(steps_to_move, int):
            raise Exception("ERROR in SlidingWindow, move_window():Index steps_to_move must be an Integer")

        new_window = []

        for j in range(steps_to_move, self.window_size):
            new_window.append(self.window[j])

        for i in range(self.data_start_index, (self.window_size - len(new_window)) + self.data_start_index):
            if i >= len(self.data_list):
                new_window.append({"data": None, "seq": None})
            else:
                new_window.append({"data": self.data_list[i],
                                   "seq": self.possible_sequence_numbers[i % (2 * self.window_size)]})
            self.data_start_index += 1

        self.window = new_window

    def get_sequence_number(self, window_index):
        """Entrega el número de secuencia del elemento almacenado en la posición
        window_index de la ventana."""

        try:
            return self.window[window_index]["seq"]
        except IndexError:
            raise Exception("ERROR in SlidingWindow, get_sequence_number(): Invalid index window_index")
        except TypeError:
            raise Exception("ERROR in SlidingWindow, get_sequence_number(): Index window_index must be an Integer")

    def get_data(self, window_index):
        """Entrega los datos contenidos en el elemento almacenado en la posición
        window_index de la ventana."""

        try:
            return self.window[window_index]["data"]
        except IndexError:
            raise Exception("ERROR in SlidingWindow, get_data(): Invalid index window_index")
        except TypeError:
            raise Exception("ERROR in SlidingWindow, get_data(): Index window_index must be an Integer")

    def put_data(self, data, seq, window_index):
        """Añade un elemento a la ventana en la posición window_index con
        datos=data, número de secuencia seq. Note que si la ventana no es vacía
        tiene que asegurarse que el número de secuencia sea válido dentro de la
        ventana."""

        if not isinstance(seq, int):
            raise Exception("ERROR in SlidingWindow, put_data(): Variable seq must be an Integer")
        if seq not in self.possible_sequence_numbers:
            raise Exception("ERROR in SlidingWindow, put_data(): Variable seq must belong to [Y+0, Y+2N-1]")

        try:
            current_seq_numbers = [self.get_sequence_number(i) for i in range(self.window_size) if self.get_sequence_number(i) is not None]
            if len(current_seq_numbers) == self.window_size:
                if seq != current_seq_numbers[window_index]:
                        raise Exception("ERROR in SlidingWindow, put_data(): Window is not empty, invalid sequence number")
            else:
                for existing_seq_index in range(self.window_size):
                    if self.window[existing_seq_index]["seq"] is not None:
                        existing_seq = self.window[existing_seq_index]["seq"]
                        j = self.possible_sequence_numbers.index(existing_seq)
                        valid_range = []
                        for i in reversed(range(existing_seq_index)):
                            next_index = (j - 1 - i) % len(self.possible_sequence_numbers)
                            append_seq = self.possible_sequence_numbers[next_index]
                            valid_range.append(append_seq)

                        valid_range.append(existing_seq)

                        for k in range(self.window_size - existing_seq_index - 1):
                            next_index = (j + 1 + k) % len(self.possible_sequence_numbers)
                            append_seq = self.possible_sequence_numbers[next_index]
                            valid_range.append(append_seq)
                        if seq != valid_range[window_index]:
                            raise Exception("ERROR in SlidingWindow, put_data(): Window is not empty, invalid sequence number")
            self.window[window_index]["data"] = data
            self.window[window_index]["seq"] = seq
        except IndexError:
            raise Exception("ERROR in SlidingWindow, put_data(): Invalid index window_index")
        except TypeError:
            raise Exception("ERROR in SlidingWindow, put_data(): Index window_index must be an Integer")

    def __str__(self):
        max_len = 0
        separator_line = "+------+"
        data_line = "| Data |"
        seq_line = "| Seq  |"
        for wnd_element in self.window:
            str_data = str(wnd_element["data"])
            if isinstance(wnd_element["seq"], int):
                str_seq = "Y+{} = {}".format(wnd_element["seq"] - self.initial_seq, wnd_element["seq"])
            else:
                str_seq = "None"
            if max(len(str_data), len(str_seq)) > max_len:
                max_len = max(len(str_data), len(str_seq))
            if max_len > 20:
                max_len = 20
                break

        add_to_separator = "--"
        for i in range(max_len):
            add_to_separator += "-"
        add_to_separator += "+"

        for j in range(self.window_size):
            separator_line += add_to_separator

            data_str = str(self.get_data(j))
            if len(data_str) > max_len:
                data_str = data_str[0:max_len - 5] + "(...)"
            else:
                data_str = str(self.get_data(j))
            data_line += " {}".format(data_str)
            for i in range(max_len - len(data_str)):
                data_line += " "
            data_line += " |"

            if self.get_sequence_number(j) is not None:
                seq_str = "Y+{} = {}".format(self.get_sequence_number(j) - self.initial_seq, self.get_sequence_number(j))
            else:
                seq_str = "None"
            if len(seq_str) > max_len:
                seq_str = seq_str[0:max_len - 5] + "(...)"
            seq_line += " {}".format(seq_str)
            for i in range(max_len - len(seq_str)):
                seq_line += " "
            seq_line += " |"
        data_line += "\n"
        seq_line += "\n"

        return separator_line + "\n" + data_line + separator_line + "\n" + seq_line + separator_line

