import numpy as np

class Simulation():

    def __init__(self):
        #SYSTEM VARIABLES
        self.BUSY=1
        self.IDLE=0
        self.MAX_CARS_DELAYED=0
        self.POLICE_ARRIVAL=1
        self.PARTICULAR_ARRIVAL=2
        self.DEPARTURE=3
        self.POLICE_DEPARTURE=4
        self.PARTICULAR_DEPARTURE=5
        self.generator=np.random.default_rng(30)
        #SIMULATION TIME
        self.clock=0
        #STATE VARIABLES
        self.cars_attended=0
        self.police_attended=0
        self.particular_attended=0
        self.cars_in_q=0
        self.server_status=self.IDLE
        self.nextEvent_type=0
        self.arrivals=[{"time":1e20,"type":None}]*2
        self.nextEvents_time= [{"type":None,"time":1e20}]*4
        self.time_lastEvent=0
        #ACUMULADORES
        self.police_total_delay=0
        self.particular_total_delay=0
        self.server_status_area=0
        self.police_delay_area=0
        self.particular_delay_area=0
        self.cars_in_q_area=0
        # ---------------------------------
        #READ INPUT VARIABLES AND WRITE FIRST OUTPUT
        with open("mm1.in","r") as infile:  
            self.mean_interrarival, self.mean_service, self.MAX_CARS_DELAYED = map(float,infile.read().split(" "))
        self.MAX_CARS_DELAYED = int(self.MAX_CARS_DELAYED)

        with open("mm1.out","w") as outfile:
            outfile.write("Single Queue system simulation (Gas station)\n")
        outfile=open("mm1.out","a")
        outfile.writelines(f"Mean interrarival: {self.mean_interrarival}\n Mean  service: {self.mean_service}\n")
        outfile.writelines(f"Cars delayed: {self.MAX_CARS_DELAYED}")
        # ---------------------------------
        #PROGRAM FIRST EVENTS
        self.nextEvents_time[self.POLICE_ARRIVAL] = {"type":self.POLICE_ARRIVAL,"time":15}
        time_expon =self.clock+self.expon(self.mean_interrarival)
        self.nextEvents_time[self.PARTICULAR_ARRIVAL] = {"type":self.PARTICULAR_ARRIVAL,"time":time_expon}

    def main(self):
        while self.cars_attended<self.MAX_CARS_DELAYED:
            self.timing()
            
            if self.nextEvent_type["type"]==self.POLICE_ARRIVAL:
                self.arrival_police()
            elif self.nextEvent_type["type"]==self.PARTICULAR_ARRIVAL:
                self.arrival_particular()
            elif self.nextEvent_type["type"]==self.DEPARTURE:
                self.departure()
            
            self.update_stats()
        self.generate_report()
        
    def expon(self,mean):
        return self.generator.exponential(mean)

    def timing(self):
        #print(self.nextEvents_time)
        self.nextEvent_type=min(self.nextEvents_time, key=lambda x:x["time"])
        self.clock=self.nextEvent_type["time"]

    def arrival_police(self):
        #Programar siguiente llegada de carro de policia
        next={"type":self.POLICE_ARRIVAL,"time":self.clock+30}
        self.nextEvents_time[self.POLICE_ARRIVAL] = next
        #Ver ocupacíon del servidor
        if self.server_status == self.IDLE:
            #computar demora, ocupar sevidor, aumentar cars attended
            delay=0
            self.police_total_delay+=delay
            self.server_status=self.BUSY
            self.cars_attended+=1
            self.police_attended+=1
            #programar evento de salida
            time_next=self.clock+30
            departure_police = {"type":self.DEPARTURE,"depart ":self.POLICE_DEPARTURE,"time":time_next}
            self.nextEvents_time[self.DEPARTURE] = departure_police
        elif self.server_status == self.BUSY:
            #Aumentar cola
            self.cars_in_q+=1
            #Añadir a lista de llegadas
            arrival={"time":self.clock,"type":self.POLICE_DEPARTURE}
            self.arrivals.insert(1,arrival)

    def arrival_particular(self):
        #Programar siguiente llegada de carro particular
        next={"type":self.PARTICULAR_ARRIVAL,"time":self.clock+self.expon(self.mean_interrarival)}
        self.nextEvents_time[self.PARTICULAR_ARRIVAL] = next 
        #Ver ocupacíon del servidor
        if self.server_status == self.IDLE:
            #computar demora, ocupar sevidor, aumentar cars attended
            delay=0
            self.particular_total_delay+=delay
            self.server_status=self.BUSY
            self.cars_attended+=1
            self.particular_attended+=1
            #programar evento de salida
            time_next=self.clock+self.expon(self.mean_interrarival)
            departure_particular = {"type":self.DEPARTURE,"depart ":self.PARTICULAR_DEPARTURE,"time":time_next}
            self.nextEvents_time[self.DEPARTURE] = departure_particular
        elif self.server_status == self.BUSY:
            #Aumentar cola
            self.cars_in_q+=1
            #Añadir a lista de llegadas
            arrival={"time":self.clock,"type":self.PARTICULAR_DEPARTURE}
            self.arrivals.insert(self.cars_in_q,arrival)

    def departure(self):
        if self.cars_in_q==0:
            #desocupar servidor y programar siguiente departure
            self.server_status=self.IDLE
            self.nextEvents_time[self.DEPARTURE] = {"type":self.DEPARTURE,"time":1e20}
        else:
            #Disminuir la cola y sumar demora en la cola
            self.cars_in_q-=1
            delay=self.clock-self.arrivals[1]["time"]
            next_car=self.arrivals[1]["type"]
            next_time=self.clock+self.expon(self.mean_service)
            
            if next_car==self.POLICE_DEPARTURE:
                self.police_total_delay+=delay
                next_event= {"type":self.DEPARTURE,"depart ":self.POLICE_DEPARTURE,"time":next_time}
                self.nextEvent_type[self.DEPARTURE]=next_event
                self.police_attended+=1
            elif next_car==self.PARTICULAR_DEPARTURE:
                self.particular_total_delay+=delay
                next_event= {"type":self.DEPARTURE,"depart ":self.PARTICULAR_DEPARTURE,"time":next_time}
                self.particular_attended+=1
            
            #aumentar carros atendidos y quitar de lista
            self.cars_attended+=1
            self.arrivals.pop(1)

    def update_stats(self):
        #Calcular tiempo desde último evento y setear timelastEvent
        time_since_lastEvent=self.clock-self.time_lastEvent
        self.time_lastEvent=self.clock

        #Actualizar área bajo curvas
        self.cars_in_q_area+=self.cars_in_q*time_since_lastEvent

        self.server_status_area+=self.server_status*time_since_lastEvent

    def generate_report(self):
        #Calculo de promedios
        average_delay_total = (self.police_total_delay+self.particular_total_delay)/self.cars_attended
        average_delay_police = self.police_total_delay/self.police_attended
        average_delay_particular = self.particular_total_delay/self.particular_attended
        average_num_q= self.cars_in_q_area/self.clock
        average_server_occupation=self.server_status_area/self.clock

        print("Single server queueing system Gas station")
        print(f"Mean interrarrival time {self.mean_interrarival} minutes")
        print(f"Mean service time {self.mean_service} minutes")
        print(f"Number of customers {self.cars_attended}\n")

        print(f"Average delay in queue for police cars {average_delay_police:.4f} minutes")
        print(f"Average delay in queue for particular cars {average_delay_particular:.4f} minutes")
        print(f"Average number in queue {average_num_q:.4f}")
        print(f"Server utilization {average_server_occupation:.4f}")
        print(f"Time simulation ended {self.clock} minutes")

        # print("police",self.police_total_delay)
        # print("particular",self.particular_total_delay)
        # print(f"area server status {self.server_status_area}")
        # print(f"area q {self.cars_in_q_area}")

        print()

sim=Simulation()
sim.main()