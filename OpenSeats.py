"""course		name						hours	sections...		CRN	  seatstaken/total	teach			
['ACCT115', 'FUND OF FINANCIAL ACCOUNTING', 3, ['ACCT115', '002', 10001, '23 \\/ 39', 'Gomez, Steven', 0, 0, '', 'FUND OF FINANCIAL ACCOUNTING', [[3, 52200, 57000, 'KUPF 104'], [5, 52200, 57000, 'KUPF 104']]], ['ACCT115', '102', 10002, '12 \\/ 39', 'Taylor, Ming', 0, 0, '', 'FUND OF FINANCIAL ACCOUNTING', [[2, 64800, 75000, 'KUPF 105']]], ['ACCT115', '104', 10003, '15 \\/ 39', 'Gomez, Steven', 0, 0, '', 'FUND OF FINANCIAL ACCOUNTING', [[5, 64800, 75000, 'TIER 105']]]]
"""
import requests
import tkinter as tk
import json
import re
import sys
from datetime import datetime
import time
import smtplib # Import smtplib for the actual sending function
from email.parser import Parser

def getEmail():
	# return ["TO@gmail.com", "FROM@gmail.com", "FROMPASSWORD"]
	root=tk.Tk() 
	root.title("NJIT Open Course Notifier")
	root.geometry("400x100")
	data_var=tk.StringVar()
	email_var=tk.StringVar()
	password_var=tk.StringVar()

	def submit(event=""):
		global data, email, password
		data=data_entry.get()
		email=email_entry.get()
		password=password_entry.get()
		print(f"email: {email}")
		print(f"password: {password}")
		  
		print("The data is : " + data)
		  
		data_var.set("")
		email_var.set("")
		password_var.set("")
		root.destroy()

	data_label = tk.Label(root, text = "Enter the email you want to be notified", 
	              font=('calibre', 
	                    10, 'bold')) 
	data_entry = tk.Entry(root, textvariable = data_var, font=('calibre',10,'normal')) 
	email_label = tk.Label(root, text = "Enter the dummy email", font=('calibre', 10, 'bold')) 
	email_entry = tk.Entry(root, textvariable = email_var, font=('calibre',10,'normal')) 
	password_label = tk.Label(root, text = "Enter the password", font=('calibre', 10, 'bold')) 
	password_entry = tk.Entry(root, show="*", textvariable = password_var, font=('calibre',10,'normal')) 

	sub_btn=tk.Button(root,text = 'Submit', 
	          command = submit)
	data_entry.focus_set()
   
	# placing the label and entry in 
	# the required position using grid 
	# method 
	data_label.grid(row=0,column=0) 
	data_entry.grid(row=0,column=1) 
	email_label.grid(row=1,column=0)
	email_entry.grid(row=1,column=1) 
	password_label.grid(row=2,column=0)
	password_entry.grid(row=2,column=1) 

	sub_btn.grid(row=3,column=1)
	root.bind("<Return>", submit)
	   
	# performing an infinite loop  
	# for the window to display 
	root.mainloop()
	return [data, email, password]

def isOpen(string):
	global mySections, seatsOpen
	capture = re.search("(\\d*) \\\\/ (\\d*)", string)
	seatsTaken = capture[1]
	seatsAvail = capture[2]
	seatsOpen = int(seatsAvail) - int(seatsTaken)

	if seatsOpen > 0:
		return True
	return False

def printInfo(section):
	for i in range(0, len(section)):
		print(f"i:{i}, course:{section[i]}")

def getSections(course):
	sections = []
	for z in range(3, len(course)):#iterate through course sections
		section = course[z]
		sections.append(course[z][1])
	return sections

def emailMe(section):
	global mySections, seatsOpen, EMAIL, FROM, PASSWORD
	print(f"Sending email about course {section[0]} section {section[1]}")

	subject = f"{section[0]}, {section[1]} has {seatsOpen} seat open!"
	body = f"GO REGISTER NOW: http://myhub.njit.edu/StudentRegistrationSsb/ssb/registration/registration"

	message = f"Subject: {subject}\n\n {body}"
	server = smtplib.SMTP("smtp.gmail.com", 587)
	server.ehlo()
	server.starttls()
	server.login(FROM, PASSWORD)
	                #(FROM, TO, MESSAGE)
	server.sendmail(FROM, EMAIL, message)
	server.quit()

def scrapeData():
	global mySections, COURSELIST
	print(f"Scraping latest data at " + datetime.now().strftime("%I:%M:%S %p"))
	req = requests.get(f'https://uisapppr3.njit.edu/scbldr/include/datasvc.php?p=/')
	# print(req.text)
	text = req.text[15:-53] #fix this for when term changes... fall[15:-53] -> spring[15:-55]
	# print(text)
	# print(text[0:1000])
	null = None
	false = False
	COURSELIST = eval(text)

def parseClasses():
	global mySections, COURSELIST
	print("Parsing...")
	for course in COURSELIST:
		if course[0] in mySections.keys():
			for z in range(3, len(course)):#iterate through course sections
				section = course[z]
				# printInfo(section)
				if section[1] in mySections[course[0]]:
					if isOpen(section[3]):
						try:
							emailMe(section)
						except:
							raise Exception("Invalid email credentials")
					# else:
					# 	print(f"No seats open for {section[0]} {section[1]}")

def chooseClasses():
	global mySections, COURSELIST, sub_btn, RUN
	mySections = {}
	RUN = False
	root=tk.Tk()
	root.title("NJIT Open Seat Notifier")
	root.geometry("500x400")

	def restart():
		scrapeData()
		run()

	def stop(event=""):
		global run_btn, RUN
		print("STOPPING")
		RUN = False
		run_btn.grid_forget()
		run_btn = tk.Button(root, text = "RUN", command = run)
		run_btn.grid(row=20, column=2)

	def run(event=""):
		global run_btn, RUN, minutes
		print("RUNNING")
		RUN = True
		run_btn.grid_forget()
		run_btn = tk.Button(root, text = "STOP", command = stop)
		run_btn.grid(row=20,column=2)
		
		parseClasses()
		print(f"Waiting {minutes} minutes, then retry...")
		# time.sleep(minutes*60) #wait x minutes, then do it AGAIN!
		# scrapeData()
		run_btn.after(minutes*60000, restart)

	def back(event=""):
		global section_labels, section_vars, RUN, back_btn, run_btn
		run_btn = tk.Button(root, text = "RUN", command = run)
		if RUN:
			stop()
		for checkmark in section_labels:
			checkmark.grid_forget()
		section_labels = []
		section_vars = []
		# submit("", course_choice)
		back_btn.grid_forget()
		if mySections:
			run_btn.grid(row=20,column=2)
		else:
			run_btn.grid_forget()

		render()

	def submitSections(event=""):
		global course_choice, section_labels, section_vars, sections
		# for x in section_vars:CS370
		# 	print(x.get())
		# for x in sections:
		# 	print(x)
		for i in range(0, len(sections)):
			if section_vars[i].get() == 1:
				if course_choice not in mySections:
					mySections[course_choice] = [sections[i]]
				else:
					mySections[course_choice].append(sections[i])
		print(mySections)
		back()

	def submit(event=""):
		global sub_btn, section_labels, section_vars, sections, course_entry, course_label, course_var, course_choice, run_btn, back_btn
		section_labels = []
		section_vars = []
		course_choice=course_entry.get().upper()
		# populate sections
		for course in COURSELIST:
			if course[0] == course_choice:
				course_entry.grid_forget()
				sub_btn.grid_forget()
				back_btn = tk.Button(root, text = "Back", command = back)
				sub_btn = tk.Button(root, text = 'Add Sections', command = submitSections)
				back_btn.grid(row=20, column=0)
				sub_btn.grid(row=20,column=1)
				sections = getSections(course)
				course_label["text"] = f"Which sections would you like? ({course_choice})"
				
				# todo:
				# for setting sections red when full
				# for thing in course:
				# 	if type(thing) == list and thing[0] == course_label:
				# 		print(thing)

				for index, section in enumerate(sections):
					section_vars.append(tk.IntVar())
					section_labels.append(tk.Checkbutton(root, text=section, variable=section_vars[index], font=('calibre', 10, 'bold')))
				for i in range(0, len(section_labels)):
					section_labels[i].grid(row=i+1, column=0)

				# while section_choice != "":
				# 	for section in sections:
				# 		section_labels.append(tk.Label(root, text=section, font=('calibre', 10, 'bold')))
		course_var.set("")
	
	def render():
		global course_entry, course_label, course_var, sub_btn, run_btn

		course_var = tk.StringVar()

		course_label = tk.Label(root, text="Which course would you like? (ex: 'CS341')", font=('calibre', 10, 'bold'))
		course_label.grid(row=0, column=0)

		course_entry = tk.Entry(root, textvariable=course_var, font=('calibre', 10, 'bold'))
		course_entry.grid(row=0, column=1)
		
		sub_btn=tk.Button(root,text = 'Search Courses', command = submit)
		sub_btn.grid(row=20,column=1)
		

				
		root.bind("<Return>", submit)
		   
		# performing an infinite loop  
		# for the window to display 
		root.mainloop()
	render()
	##########################################
	print(f"mySections: {mySections}")

if __name__ == "__main__":
	# count = 0
	minutes = 1
	EMAIL, FROM, PASSWORD = getEmail()
	scrapeData()
	chooseClasses()