#Importación de librerias
import numpy as np

#Declaración de variables del sistema
BUSY=1
IDLE=0
POLICE_CAR=1
PARTICULAR_CAR=2
DEPARTURE=3
MAX_CARS_DELAYED=None

#int variables
next_event_type=cars_delayed=cars_in_q=server_status= None

#float variables
sim_time=area_server_status=area_q_police=area_q_particular=mean_interrarival=mean_service=time_last_event=total_delays_police=total_delays_particular=min_time_next_event = None

#arrays
time_arrival=[]
time_next_event=[1e20]*5


#Declaración de rutinas

def initialize():pass
def timing():pass
def arrival_police():pass
def arrival_particular():pass
def departure_police():pass
def departure_particular():pass
def statistics_update():pass
def generate_report():pass
def expon():pass

## Rutina principal

def main():
    global mean_interrarival
    global mean_service
    global time_arrival
    global total_delays_particular
    global total_delays_police
    global area_server_status

    #Leer variables de entrada
    with open("mm1.in","r") as infile:  
        mean_interrarival, mean_service, MAX_CARS_DELAYED = infile.read().split(" ")
        mean_interrarival=float(mean_interrarival)
        mean_service= float(mean_service)
        MAX_CARS_DELAYED = int(MAX_CARS_DELAYED)

    with open("mm1.out","w") as outfile:
        outfile.write("Single Queue system simulation (Gas station)\n")
    
    outfile=open("mm1.out","a")
    outfile.writelines(f"Mean interrarival: {mean_interrarival}\n Mean service: {mean_service}\n")
    outfile.writelines(f"Cars delayed: {MAX_CARS_DELAYED}")
    initialize()

    #print(time_arrival)
    while cars_delayed < 20: #MAX_CARS_DELAYED:
        timing()

        if next_event_type==POLICE_CAR:
            arrival_police()
        elif next_event_type==PARTICULAR_CAR:
            arrival_particular()
        elif next_event_type==DEPARTURE:
            departure()
    
    print("delay police", total_delays_police)
    print("delay particulars", total_delays_particular)
    #     statistics_update()

    # generate_report()
        
## Rutina de inicializacion

def initialize():
    global sim_time
    global server_status
    global cars_in_q
    global area_q_particular
    global area_server_status
    global area_q_police
    global time_last_event
    global total_delays_police
    global total_delays_particular
    global cars_delayed
    global next_event_type
    global min_time_next_event

    #Inicializar reloj del sistema a 0
    sim_time=0 

    #Inicializar variables del sistema
    server_status=IDLE
    cars_in_q=0
    time_last_event=0
    min_time_next_event=0
    #Inicializar variable estadísticas
    area_server_status=area_q_police=area_q_particular=cars_delayed=total_delays_police=total_delays_particular=0

    #Incializar lista de eventos
    time_next_event[POLICE_CAR]=15
    time_next_event[PARTICULAR_CAR]=sim_time+expon(mean_interrarival)
    print("first particular arrival",time_next_event[PARTICULAR_CAR])

def expon(mean):
    generator=np.random.default_rng()
    return generator.exponential(scale=mean)

def timing():
    global time_next_event
    global next_event_type
    global sim_time
    global min_time_next_event
    next_event_type=0

    min_time_next_event = min(time_next_event)
    next_event_type=time_next_event.index(min_time_next_event)
    sim_time=min_time_next_event

    if next_event_type==0:
        print("lista de eventos vacía")
        exit(1)
    # print(f"simulation time is: {sim_time}\n")
    # print(time_next_event)
    #print(f"\n next event type is: {next_event_type} \n")

def arrival_police():
    global time_next_event
    global sim_time
    global server_status
    global total_delays_police
    global cars_delayed
    global mean_service
    global cars_in_q
    # Programar siguiente llegada de carro de policia
    time_next_event[POLICE_CAR] = sim_time + 30
    print(server_status)

    #Ver ocupación del servidor 
    if server_status==IDLE:
        #sacar demora y sumarla al total
        delay=0
        total_delays_police+=delay
        #ocupar al servidor y aumentar carros que completaron la demora
        server_status=BUSY
        cars_delayed+=1
        #Programar departure
        time_next_event[DEPARTURE]=sim_time+expon(mean_service)   
    elif server_status==BUSY:
        cars_in_q+=1
        #print(f"cars in q: {cars_in_q}")
        arrival={"time":sim_time,"type":POLICE_CAR}
        time_arrival.insert(1,arrival)

def arrival_particular():
    global time_next_event
    global sim_time
    global server_status
    global total_delays_particular
    global cars_delayed
    global mean_service
    global cars_in_q
    global mean_interrarival
    # Programar siguiente llegada de carro particular
    time_next_event[PARTICULAR_CAR] = sim_time + expon(mean_interrarival)
    time_next_event[PARTICULAR_CAR]

    #Ver ocupación del servidor 
    if server_status==IDLE:
        delay=0
        total_delays_particular+=delay
        server_status=BUSY
        cars_delayed+=1
        time_next_event[DEPARTURE]=sim_time+expon(mean_service)   
    elif server_status==BUSY:
        cars_in_q+=1
        #print(f"cars in q: {cars_in_q}")
        arrival={"time":sim_time,"type":PARTICULAR_CAR}
        time_arrival.insert(cars_in_q,arrival)

def departure():
    global sim_time
    global cars_in_q
    global server_status
    global time_next_event
    global time_arrival
    global next_event_type
    global total_delays_police
    global total_delays_particular
    global cars_delayed
    global mean_service

    if cars_in_q ==0:
        #marcar al servidor libre
        server_status=IDLE
        time_next_event[DEPARTURE] = 1e20
    else:
        next_car_type=time_arrival[0]["type"]
        #disminuir la cola 
        cars_in_q-=1
        #Calcular demora y sumarla
        delay=sim_time-time_arrival[0]["time"]
        if next_car_type==POLICE_CAR:
            total_delays_police+=delay
            #Programar salida
            time_next_event[DEPARTURE] = expon(mean_service)
        elif next_car_type==PARTICULAR_CAR:
            total_delays_particular+=delay
            #Programar salida
            time_next_event[DEPARTURE] = expon(mean_service)
        #Aumentar carros atentidos
        cars_delayed+=1
        time_arrival.pop(0)
        



main()
