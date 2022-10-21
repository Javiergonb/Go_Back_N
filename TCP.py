
import socket
import random


from sqlalchemy import true
import slidingWindow as sw
import timerList as tm

loss_percentage = 0

class SocketTCP():
    def __init__(self):
        self.socketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.destinyAddress = None
        self.originAddress = None
        self.seqNumber = None
        self.recievedMessage = ""
        self.notRecieved = ""
        self.buffsize = 16
        self.messageLength = 0


    @staticmethod
    def parse_segment(headers):
        #separamos los headers
        headerlist = headers.split("|||")
        #guardamos cada elemento 
        syn = headerlist[0]
        ack = headerlist[1]
        fin = headerlist[2]
        seq = headerlist[3]
        datos = headerlist[4]

        #creamos el diccionario
        headers = {"SYN":syn,"ACK":ack,"FIN":fin,"SEQ":seq,"DATOS":datos}
        return headers
    @staticmethod
    def create_segment(dict):
        string = ""
        for data in dict.values():
            if data == "":
                break
            string+= data
            string += "|||"

        return string

    @staticmethod
    def is_valid_ack_go_back_n(self,current,answer):
        current = self.parse_segment(current)
        answer = self.parse_segment(answer)
        if current["SEQ"] == answer["SEQ"]:

            return True
        else:
            
            return False
    @staticmethod
    def send_con_perdidas(socket, address, message_in_bytes, loss_probability):
        # sacamos un número entre 0 y 100 de forma aleatoria
        random_number = random.randint(0, 100)
        # si el random_number es mayor o igual a la probabilidad de perdida enviamos el mensaje
        if random_number >= loss_probability:
            socket.sendto(message_in_bytes, address)
        else:
            print("oh no, pérdida de: {}".format(message_in_bytes))
    
    @staticmethod
    def recv_con_perdidas(socket, buff_size, loss_probability):
        while True:
            # recibimos el mensaje y su dirección de origen
            buffer, address = socket.recvfrom(buff_size)
            # sacamos un número entre 0 y 100 de forma aleatoria
            random_number = random.randint(0, 100)
            # si el random_number es menor o igual a la probabilidad de perdida omitimos el mensaje (hacemos como que no llegó)
            if random_number <= loss_probability:
                continue
            # de lo contrario salimos del loop y retornamos
            else:
                break
        return buffer, address

    @staticmethod
    def separte_message_parts(message):
        n = 16	# every 16 bytes
        split_string = [message[i:i+n] for i in range(0, len(message), n)]
        return split_string
    @staticmethod
    def make_headers(syn,ack,fin,seq,datos):
        return str(syn) + "|||" + str(ack) + "|||" + str(fin) + "|||" + str(seq) + "|||" + datos

   


    def bind(self,address):
        #we bind the socket to the adress
        self.socketUDP.bind(address)
        #Save the adress we are binded to if we need it for later
        self.originAddress = address
    
    def connect(self,address):
        self.socketUDP.settimeout(1)
        #random sequence number
        self.seqNumber = random.randint(0,100)
        #Create the message we are going to send
        
        #send the SYN message with seq
        syn_seq_message = "1|||0|||0|||" + str(self.seqNumber) + "|||" 
       
        #We try to send the message
        self.send_con_perdidas(self.socketUDP,address,syn_seq_message.encode(),loss_percentage)
        #We set acknowledged to False
        acknowledged = False
        while not acknowledged:
            try:
                response_seq_plusone , destiny_address = self.recv_con_perdidas(self.socketUDP,1024,loss_percentage)
                
                response_dict = self.parse_segment(response_seq_plusone.decode())
                if response_dict["SEQ"] == str(self.seqNumber + 1):
                    acknowledged = True
            except socket.timeout:
                self.send_con_perdidas(self.socketUDP,address,syn_seq_message.encode(),loss_percentage)

        #recieve the message from the server
        self.destinyAddress = destiny_address
        #We acknowledge the connection
        message_seq_plus_two = "0|||1|||0|||" + str(int(self.seqNumber) + 2) + "|||"
        #We change the seq number to x + 2
        
        #we send the message
        self.send_con_perdidas(self.socketUDP,self.destinyAddress,message_seq_plus_two.encode(),loss_percentage)
        

    def accept(self):

        #We recieve the message from the client
        message_seq , destiny_address = self.recv_con_perdidas(self.socketUDP,1024,loss_percentage)
    
        #We parse the message
        message_seq_dict = self.parse_segment(message_seq.decode())

        #Create a new socket where we will send messages to the client
        new_socket = SocketTCP()

        #We bind the new socket to an adress
        new_address = ("localhost",5003)
        new_socket.bind(new_address)

        #we set the destiny and origin adresses
        new_socket.originAddress = new_address
        new_socket.destinyAddress = destiny_address
        
        #We set the new sockets sequence number
        new_socket.seqNumber = int(message_seq_dict["SEQ"])

        #We respond with a SYN + ACK with a SEQ + 1
        response_seq_plus_one = "1|||1|||0|||" + str(int(message_seq_dict["SEQ"]) + 1) + "|||"
        #We set a timeout for our new socket
        new_socket.socketUDP.settimeout(0.5)

        #We send the message that we have recieved something and we send seq plus one
        new_socket.send_con_perdidas(new_socket.socketUDP,new_socket.destinyAddress,response_seq_plus_one.encode(),loss_percentage)
        #acknowledged set to False
        acknowledged = False
        while not acknowledged:
            try:
                #we wait to recieve a message
                ack_seq_plus_two , _ = new_socket.recv_con_perdidas(new_socket.socketUDP,1024,loss_percentage)
                ack_dict = self.parse_segment(ack_seq_plus_two.decode())
               
                #Final ack message was recieved
                if ack_dict["SEQ"] == str(new_socket.seqNumber + 2):
                    acknowledged = True
                #ACK message was lost and a message was recieved instead
                elif ack_dict["ACK"] == "0" and ack_dict["SYN"] == "0" and len(ack_dict["DATOS"]) != 0:
                    
                    
                    #We get the message lenght in bytes
                    message_length_bytes = len(ack_dict["DATOS"].encode())
                    #we set the actual message length
                    new_socket.messageLength = int(ack_dict["DATOS"])
                    #we set the new sequence numbre
                    seq = int(ack_dict["SEQ"]) + message_length_bytes
                    response = "0|||1|||0|||" + str(seq) + "|||"
                    #we respond
                    self.send_con_perdidas(new_socket.socketUDP,new_socket.destinyAddress,response.encode(),loss_percentage)
                    


            except socket.timeout:
                #We send it again incase it was lost
                new_socket.send_con_perdidas(new_socket.socketUDP,new_socket.destinyAddress,response_seq_plus_one.encode(),loss_percentage)

        #we return the new socket   
        return new_socket , new_socket.originAddress

    
    def send(self,message,mode = "stop&wait"):
        if mode == "stop&wait":
            self.send_using_stop_and_wait(message)
       

    def recv(self,buff_size,mode = "stop&wait"):
        if mode == "stop&wait":
            self.recv_using_stop_and_wait(buff_size)
       
            
    def close(self):
        self.socketUDP.settimeout(3)

        seq = self.seqNumber

        close_message = "0|||0|||1|||" + str(seq) + "|||"
        #we send the closing message
        self.socketUDP.sendto(close_message.encode(),self.destinyAddress)
        #we try to recieve the acknowledgement
        try:
            end_message , _ = self.socketUDP.recvfrom(1024)
        except:
            print("Nothing was ACKnowledged and FINalized")


        ending_message_response = "0|||1|||0|||" + str(seq + 2) + "|||"
        #we send the message that we got the ack
        self.socketUDP.sendto(ending_message_response.encode(),self.destinyAddress)
        #we close the connection
        self.socketUDP.close()
        return

    def send_using_stop_and_wait(self,message):

        self.socketUDP.settimeout(5)
        #we get the length of the message 
        length = len(message.decode())
        #we get the length in bytes
        length_in_bytes = len(str(length))
        #we set the sequence number to the one saved in the object instance
        seq = self.seqNumber
        
        #we get the first message with the message length
        first_message = "0|||0|||0|||" + str(seq) + "|||" + str(length)
        
        #we send the message
        self.socketUDP.sendto(first_message.encode(),self.destinyAddress)#Añade headers al mensaje headers.Message !!

        
        try:   
            #we wait for a response
            response1 , _ = self.socketUDP.recvfrom(1024)

            

        except socket.timeout:
            print("Error Nothing was ACKnowledged")
            return
        
        #if we get a respone que parse the message
        response1_dict = self.parse_segment(response1.decode())
        #set the seq to the answer
        seq = response1_dict["SEQ"]
        #we create the message sent so far as nothing
        message_sent_so_far = ''.encode()
        #we set the inital byte
        byte_inicial = 0

        # dentro del ciclo cortamos el mensaje en trozos de tamaño receiver_buff_size
        while True:
            # max_byte indica "hasta que byte" vamos a enviar, lo seteamos para evitar tratar de mandar más de lo que es posible
            max_byte = min(len(message), byte_inicial + self.buffsize)
    
            # obtenemos el trozo de mensaje
            message_slice = message[byte_inicial: max_byte]

            message_slice_TCP = "0|||0|||0|||" + str(seq) + "|||" + message_slice.decode()
            #we send the slice
            self.socketUDP.sendto(message_slice_TCP.encode(),self.destinyAddress)
            
            try:
                #we wait for a response
                response2 , _ = self.socketUDP.recvfrom(1024)
            except socket.timeout:
                print("Error Nothing was ACKnowledged")


            response2_dict = self.parse_segment(response2.decode())

            seq = response2_dict["SEQ"]

            # actualizamos cuánto hemos mandado
            message_sent_so_far += message_slice

            # si encontramos el end_of_message detenemos el ciclo y retornamos pues ya se envió el mensaje completo
            if len(message_sent_so_far.decode()) == length:
                break

            # de lo contrario actualizamos el byte inicial para enviar el siguiente trozo
            byte_inicial += self.buffsize

    def recv_using_stop_and_wait(self,buff_size):

        self.socketUDP.settimeout(5)
        #we set the recieved message as nothing
        recieved_message = ""
        #if this is the first time we call recv then the message length in the object will be zero
        if self.messageLength == 0:
            # we try to recive a message
            try:
                message , _ = self.socketUDP.recvfrom(1024)
            except socket.timeout:
                print("Nothing was received")
                return
            message_dict = self.parse_segment(message.decode())
            #this means we recieved a closing message
            if message_dict["FIN"] == "1":
                seq = int(message_dict["SEQ"]) 
                end_message = "0|||1|||1|||" + str(seq + 1) + "|||"
                self.socketUDP.sendto(end_message.encode(),self.destinyAddress)
                try:
                    close_message , _ = self.socketUDP.recvfrom(1024)
                    self.socketUDP.close()
                    return
                except socket.timeout:
                    print("Nothing was FINalized")
            #we get the lenght in bytes and normal length
            message_length_bytes = len(message_dict["DATOS"].encode())
            self.messageLength = int(message_dict["DATOS"])
            #set the new sequence
            seq = int(message_dict["SEQ"]) + message_length_bytes
            response = "0|||1|||0|||" + str(seq) + "|||"
            #we respond
            self.socketUDP.sendto(response.encode(), self.destinyAddress)
        while True: 
            #if there was a piece of the last slice recieved that we were not able to recieve we stitch it to the recieved message
            recieved_message += self.notRecieved
            #we reset the recieved and not recieved message
            self.notRecieved = ""
            self.recievedMessage = ""
            #we try to recieve a message
            try:
                message_while , _ = self.socketUDP.recvfrom(1024)
            except socket.timeout:
                 print("Nothing was received")
                 return
            #we recieve the message and get the necessary info
            message_while_dict = self.parse_segment(message_while.decode())
            message_while_length_bytes = len(message_while_dict["DATOS"].encode())
            message_while_data = message_while_dict["DATOS"]
            seq = int(message_while_dict["SEQ"]) + message_while_length_bytes
            response = "0|||1|||0|||" + str(seq) + "|||"
            #we responf
            self.socketUDP.sendto(response.encode(), self.destinyAddress)
            #we concatenate the slice we recieved
            recieved_message += message_while_data
            #if the slice we recieved was too long for the buff size
            if len(recieved_message.encode()) >= buff_size:
                #we save in the object the piece of the message that fits
                self.recievedMessage = recieved_message[:buff_size]
                #and we save the part that doesnt fit
                self.notRecieved = recieved_message[buff_size:]
                #we take away the lenght of the message that we recieved 
                # so we know when we are finished recieving the message in the future
                self.messageLength = self.messageLength - len(self.recievedMessage)
                break
            #if the message we have recieved so far is the length we recieved
            if len(recieved_message) == self.messageLength:
                #we save the recieved message
                self.recievedMessage = recieved_message
                #we reset the variable so we may recieve new messages
                self.messageLength = 0
                break
            else:
                #if we are still recieving slices
                # then we continue
                continue

    def send_using_go_back_n(self,message):
        #we set the window size to 3
        window_size = 3
       
        #we set the seq number to the saved one in the object
        initial_seq = self.seqNumber
        #we get the message length
        message_length = len(message.encode())
        
        #we separate the message in 16 bytes slices
        separated_message = self.separte_message_parts(message)
        
        #we create the data we are going to send
        data_list = [message_length] + separated_message
        
        #timeout
        timeout = 2
        
        #creamos la sliding window
        data_window = sw.SlidingWindow(window_size, data_list, initial_seq)
        base_index = 0
        next_send_index = 0
        wnd_index = 0
        
        
        # creamos un timer usando TimerList
        timer_list = tm.TimerList(self.timeout, len(data_list))
        t_index = 0

        
        timer_list.start_timer(t_index)
        # para poder usar este timer vamos poner nuestro socket como no bloqueante
        self.socket_udp.setblocking(False)
        
       
        while base_index < len(data_list):
            #mandamos todo lo que hay en la ventana
            while next_send_index < base_index + window_size:
                sending_data = data_window.get_data(next_send_index)
                sending_seq = data_window.get_sequence_number(next_send_index)
                sending_segment = self.make_headers(0,0,0,sending_seq,sending_data)
                print("Mandando paquete" + next_send_index)
                self.socket_udp.sendto(sending_segment.encode(), self.destination_address)
                next_send_index += 1
            
            try:
                # en cada iteración vemos si nuestro timer hizo timeout
                timeouts = timer_list.get_timed_out_timers()
                # si hizo timeout reenviamos el último segmento
                if len(timeouts) > 0:
                    #reiniciamos el siguiente a mandar
                    wnd_index = base_index
                    # reiniciamos el timer
                    timer_list.start_timer(t_index)

                # si no hubo timeout esperamos el ack del receptor
                answer, _ = self.socket_udp.recvfrom(self.buff_size)
            except BlockingIOError:
                 # como nuestro socket no es bloqueante, si no llega nada entramos aquí y continuamos (hacemos esto en vez de usar threads)
                 continue
            #recibimos algo 
            else:

                # si no entramos al except (y no hubo otro error) significa que llegó algo!
                # si la respuesta es un ack válido
                current_data = data_window.get_data(wnd_index)
                current_seq = data_window.get_sequence_number(wnd_index)
                current_segment = self.make_headers(0,0,0,current_seq,current_data)
                #we check if the ack we recieved is valid
                if self.is_valid_ack_go_back_n(current_segment, answer.decode()):
                    #si es valido movemos la ventana por uno
                    data_window.move_window(1)
                    base += 1
                    next_send_index += 1
                    wnd_index += 1
                    current_data = data_window.get_data(wnd_index)

                    # si ya mandamos el mensaje completo tenemos current_data == None
                    if current_data == None:
                        return

                    else:
                        current_seq = data_window.get_sequence_number(wnd_index)
                        self.seq = current_seq
                        current_segment = self.make_headers(0,0,0,current_seq,current_data)
                        self.socket_udp.sendto(current_segment.encode(), self.destination_address)
                    
                        # y ponemos a correr de nuevo el timer
                        timer_list.start_timer(t_index)