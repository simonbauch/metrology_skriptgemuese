import pyvisa
import time
import datetime
import numpy
import csv
import matplotlib.pyplot as plt
rm = pyvisa.ResourceManager()
# print(rm.list_resources())
inst1 = rm.open_resource('visa://172.23.0.30/GPIB0::22::INSTR') #34401A 1
inst2 = rm.open_resource('visa://172.23.0.30/GPIB0::23::INSTR') #34401A 2
inst3 = rm.open_resource('visa://172.23.0.30/GPIB0::14::INSTR') #Keithley 740


print(inst1.query("*IDN?"))
print(inst2.query("*IDN?"))

inst1.write("*RST")
inst2.write("*RST")

inst1.write("DISP 0")
inst2.write("DISP 0")

#Configure Meassurement:
inst1.write("FUNC \"VOLT:DC\"") #DC-VOLT
inst2.write("FUNC \"VOLT:DC\"")

inst1.write("VOLT:DC:RANG 10") #10V Range
inst2.write("VOLT:DC:RANG 10")

inst1.write("VOLT:DC:RES MIN") #Max res
inst2.write("VOLT:DC:RES MIN")    

inst1.write("VOLT:DC:NPLC 100") #Max PLC
inst2.write("VOLT:DC:NPLC 100")   

inst1.write("SENS:ZERO:AUTO ON") #Autozero on
inst2.write("SENS:ZERO:AUTO ON")

inst1.write("INP:IMP:AUTO ON") #10GOhm imput res
inst2.write("INP:IMP:AUTO ON")   

time.sleep(30)

i=0
err=0
data1 = []
data2 = []
temp = []
te = []
timeins = []
while i<10000 and err<10:
    try:    
        inst1.write("READ?")
        inst2.write("READ?")
        time.sleep(2)
        data1.append(float(inst1.read()))
        data2.append(float(inst2.read()))
        
        te=inst3.read().split(',')        
        temp.append(float(te[0][4:]))
        
        timeins.append(datetime.datetime.now())
        
        print(data1[i])
        print(data2[i])
        print(temp[i])
        print(timeins[i])
        print(i)
        i=i+1
    except:
        print("Connection Error")
        err = err+1
        
print(data1)
print(data2)
print(err)

mean1 = numpy.mean(data1)
mean2 = numpy.mean(data2)
print(mean1)
print(mean2)

datac1 = []
datac2 = []
for x in range(0, i): #Abziehen des Mittelwertes
    #print(x)
    datac1.append(data1[x] - mean1)
    datac2.append(data2[x] - mean2)


with open(datetime.datetime.now().strftime("%Y%m%d-%H%M%S")+'.csv', 'w', newline='') as csvfile:
    fieldnames = ['Time', 'Value 1', 'Value 2', 'Value 1 norm.', 'Value 2 norm.', 'Temp']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    
    for x in range(0,i):
        writer.writerow({'Time': str(timeins[x]), 'Value 1': format(data1[x], '.8g'), 'Value 2': format(data2[x], '.8g'), 'Value 1 norm.': format(datac1[x], '.8g'), 'Value 2 norm.': format(datac2[x], '.8g'),'Temp': temp[x],})


plt.figure(1)
plt.title("Voltage over Time")
plt.plot(timeins,data1,label="MY4101XXXX")
plt.plot(timeins,data2,label="US3608XXXX")
plt.legend()
ax0 = plt.gca()
ax0.set_xlabel("Time")
plt.ylabel("Voltage in V")
ax1 = plt.twinx(ax0)
color = 'tab:red'
ax1.plot(timeins,temp, color=color)
ax1.set_ylim(15,25)
ax1.set_ylabel("Temp in °C")
plt.gcf().autofmt_xdate()


plt.figure(2)
plt.title("Voltage over Time (offset corrected)")
plt.plot(timeins,datac1,label="MY4101XXXX")
plt.plot(timeins,datac2,label="US3608XXXX")
plt.legend()
ax0 = plt.gca()
ax0.set_xlabel("Number of Samples @ 100PLC")
plt.ylabel("Voltage in V")
ax1 = plt.twinx(ax0)
color = 'tab:red'
ax1.plot(timeins,temp, color=color)
ax1.set_ylim(15,25)
ax1.set_ylabel("Temp in °C")
plt.gcf().autofmt_xdate()



plt.figure(3)
plt.title("Distribution of Samples (MY4101XXXX)")
plt.hist(datac1,bins=30)
ax = plt.gca()
ax.set_xlim([-1.5e-6, 1.5e-6])
plt.xlabel("Voltage in V")
plt.ylabel("Number of Samples @ 100PLC")

plt.figure(4)
plt.title("Distribution of Samples (US3608XXXX)")
plt.hist(datac2,bins=30)
ax = plt.gca()
ax.set_xlim([-1.5e-6, 1.5e-6])
plt.xlabel("Voltage in V")
plt.ylabel("Number of Samples @ 100PLC")

#plt.figure(5)
#plt.title("Temperature over time")
#plt.plot(temp)
#plt.xlabel("Number of Samples @ 100PLC")
#plt.ylabel("Themperature in °C")

plt.show()

#Run Self-Test

inst1.write("*TST?")
inst2.write("*TST?")
time.sleep(30)
print(inst1.read())
print(inst2.read())
