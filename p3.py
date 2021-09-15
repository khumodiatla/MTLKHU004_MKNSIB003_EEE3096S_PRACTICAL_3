# Import libraries
import RPi.GPIO as GPIO
import random
import ES2EEPROMUtils
import os
import time

# some global variables that need to change as we run the program
end_of_game = None  # set if the user wins or ends the game

# DEFINE THE PINS USED HERE
LED_value = [11, 13, 15]
LED_accuracy = 32
btn_submit = 16
btn_increase = 18
buzzer = 33
eeprom = ES2EEPROMUtils.ES2EEPROM()
guessValue = 0
fixValue = 0
count = 0
piPwm = None
piPwmBuzzer = None
eeprom.write_byte(0, count)
numberOfGuess = 0
name = ""

# Print the game banner
def welcome():
    os.system('clear')
    print("  _   _                 _                  _____ _            __  __ _")
    print("| \ | |               | |                / ____| |          / _|/ _| |")
    print("|  \| |_   _ _ __ ___ | |__   ___ _ __  | (___ | |__  _   _| |_| |_| | ___ ")
    print("| . ` | | | | '_ ` _ \| '_ \ / _ \ '__|  \___ \| '_ \| | | |  _|  _| |/ _ \\")
    print("| |\  | |_| | | | | | | |_) |  __/ |     ____) | | | | |_| | | | | | |  __/")
    print("|_| \_|\__,_|_| |_| |_|_.__/ \___|_|    |_____/|_| |_|\__,_|_| |_| |_|\___|")
    print("")
    print("Guess the number and immortalise your name in the High Score Hall of Fame!")


# Print the game menu
def menu():
    global fixValue
    global end_of_game
    option = input("Select an option:   H - View High Scores     P - Play Game       Q - Quit\n")
    option = option.upper()
    if option == "H":
        os.system('clear')
        print("HIGH SCORES!!")
        s_count, ss = fetch_scores()
        display_scores(s_count, ss)
    elif option == "P":
        os.system('clear')
        print("Starting a new round!")
        print("Use the buttons on the Pi to make and submit your guess!")
        print("Press and hold the guess button to cancel your game")
        value = generate_number()
        while not end_of_game:
	    time.sleep(0.1)
            pass
    elif option == "Q":
        print("Come back soon!")
        exit()
    else:
        print("Invalid option. Please select a valid one!")


def display_scores(count, raw_data):
    # print the scores to the screen in the expected format
    print("There are {} scores. Here are the top 3!".format(count))
    # print out the scores in the required format
    if(count == 0):
	print("1 - Empty")
	print("2 - Empty")
	print("3 - Empty")
    if(count == 1):
	print("1 - " + raw_data[0][0] + " took " + str(raw_data[0][1] + " guesses")
	print("2 - Empty")
	print("3 - Empty")
    if(count == 2):
	print("1 - " + raw_data[0][0] + " took " + str(raw_data[0][1]) + " guesses")
	print("2 - " + raw_data[1][0] + " took " + str(raw_data[1][1]) + " guesses")
	print("3 - Empty")
    if(count >= 3):	
	print("1 - " + raw_data[0][0] + " took " + str(raw_data[0][1]) + " guesses")
        print("2 - " + raw_data[1][0] + " took " + str(raw_data[1][1]) + " guesses")
	print("3 - " + raw_data[2][0] + " took " + str(raw_data[2][1]) + " guesses" )
 
# Setup Pins
def setup():
    global piPwm
    global piPwmBuzzer
    # Setup board mode
    GPIO.setmode(GPIO.BOARD)
    # Setup regular GPIO
    GPIO.setup(LED_value[0], GPIO.OUT)
    GPIO.setup(LED_value[1], GPIO.OUT)
    GPIO.setup(LED_value[2], GPIO.OUT)
    GPIO.setup(LED_accuracy, GPIO.OUT)
    GPIO.setup(buzzer, GPIO.OUT)
    GPIO.setup(btn_submit, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(btn_increase, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    # Setup PWM channels
    piPwm = GPIO.PWM(LED_accuracy, 1000)
    piPwm.start(0)
    piPwmBuzzer = GPIO.PWM(buzzer, 1000)
    # Setup debouncing and callbacks
    GPIO.add_event_detect(btn_submit, GPIO.FALLING,callback = btn_guess_pressed, bouncetime = 500)
    GPIO.add_event_detect(btn_increase, GPIO.FALLING, callback = btn_increase_pressed, bouncetime = 500)
    #initial values
    GPIO.output(buzzer, False)
    GPIO.output(LED_value[0], False)
    GPIO.output(LED_value[1], False)
    GPIO.output(LED_value[2], False)
	
# Load high scores
def fetch_scores():
    # get however many scores there are
    # Get the scores
    # convert the codes back to ascii
    # return back the results
    score_count = eeprom.read_byte(0)
    scores =  eeprom.read_block(1, score_count*4)
    array = []
    array2 = []
    i = 3
    number = score_count * 4
    while True:
	time.sleep(0.1)
	if(i >= num):
		break
	else:
		string1 = chr(scores[i-3])+""+chr(scores[i-2])+""+chr(scores[i-1])
		guess = scores[i]
		i += 4
		array.append(string1)
		array.append(guess)
    for j in  range(score_count):
	array2.append([])
    index = 0
    x = 0
    while True:
	if (x > score_count - 1):
		break
	else:
		array2[x].append(array[index])
		array2[x].append(array[index+1])	
		index += 2
		x += 1
    array2.sort(key=lambda x: x[1])
    return score_count, array2				
    #return score_count, scores
	

# Save high scores
def save_scores():
    global name
    global numberOfGuess
    global piPwm
    global piPwmBuzzer
    # fetch scores
    count, data = fetch_scores()
    count = count + 1
    data.append([])
    name = name[0:3]
    data[count -1].append(name)
    data[count -1].append(numberOfGuess)
    # include new score
    # sort
    # update total amount of scores
    eeprom.write_byte(0, count)
    scores = data
    scores.sort(key=lambda x: x[1])
    data_to_write = []
    for score in scores:
	for letter in score[0]:
		data_to_write.append(ord(letter))
	data_to_write.append(score[1])
    eeprom.write_block(1, data_to_write)
    numberOfGuess = 0
    # write new scores
   
# Generate guess number
def generate_number():
    return random.randint(0, pow(2, 3)-1)


# Increase button pressed
def btn_increase_pressed(channel):
    # Increase the value shown on the LEDs
    # You can choose to have a global variable store the user's current guess, 
    # or just pull the value off the LEDs when a user makes a guess
    global guessValue
    global piPwm
    global count
    piPwm.ChangeDutyCycle(0)
    guessValue = count
    if(count == 0):
	GPIO.output(LED_value[0],False)
	GPIO.output(LED_value[1],False)
	GPIO.output(LED_value[2],False)
    if(count == 1):
	GPIO.output(LED_value[0],True)
	GPIO.output(LED_value[1],False)
	GPIO.output(LED_value[2],False)
    if(count == 2):
	GPIO.output(LED_value[0],False)
	GPIO.output(LED_value[1],True)
	GPIO.output(LED_value[2],False)
    if(count == 3):
	GPIO.output(LED_value[0],True)
	GPIO.output(LED_value[1],True)
	GPIO.output(LED_value[2],False)
    if(count == 4):
	GPIO.output(LED_value[0],False)
	GPIO.output(LED_value[1],False)
	GPIO.output(LED_value[2],True)
    if(count == 5):
	GPIO.output(LED_value[0],True)
	GPIO.output(LED_value[1],False)
	GPIO.output(LED_value[2],True)
    if(count == 6):
	GPIO.output(LED_value[0],False)
	GPIO.output(LED_value[1],True)
	GPIO.output(LED_value[2],True)
    if(count == 7):
	GPIO.output(LED_value[0],True)
	GPIO.output(LED_value[1],True)
	GPIO.output(LED_value[2],True)
    count = count + 1
    if(count == 8):
	count = 0
    time.sleep(0.1)

# Guess button
def btn_guess_pressed(channel):
    # If they've pressed and held the button, clear up the GPIO and take them back to the menu screen
    # Compare the actual value with the user value displayed on the LEDs
    # Change the PWM LED
    # if it's close enough, adjust the buzzer
    # if it's an exact guess:
    # - Disable LEDs and Buzzer
    # - tell the user and prompt them for a name
    # - fetch all the scores
    # - add the new score
    # - sort the scores
    # - Store the scores back to the EEPROM, being sure to update the score count
    global count
    global numberOfGuess
    global piPwm
    count = 0
    numberOfGuess =  numberOfGuess + 1

    start_time = time.time()
    while(GPIO.input(channel) == 0):
	time.sleep(0.1)
    button_time = time.time() - start_time
    if(0.1 <= button_time <= 0.7):
	accuracy_leds()
	trigger_buzzer()
    if(0.7 < button_time):
	piPwm = None
	piPwmBuzzer = None
	numberOfGuess = 0
	name = ""
	GPIO.remove_event_detect(btn_submit)
	GPIO.remove_event_detect(btn_increase)
	GPIO.output(LED_value[0],False)
	GPIO.output(LED_value[1],False)
	GPIO.output(LED_value[2],False)
	GPIO.output(buzzer,False)
	GPIO.cleanup()
	setup()
	welcome()
	while True:
		time.sleep(0.1)
		menu()
		pass
	time.sleep(0.1)

# LED Brightness
def accuracy_leds():
    global piPwm
    global guessValue
    global fixValue
    # Set the brightness of the LED based on how close the guess is to the answer
    # - The % brightness should be directly proportional to the % "closeness"
    # - For example if the answer is 6 and a user guesses 4, the brightness should be at 4/6*100 = 66%
    # - If they guessed 7, the brightness would be at ((8-7)/(8-6)*100 = 50%
    dc = 0
    if(guessValue <= fixValue):
	dc = (guessValue/fixValue)*100
    else:
	dc = ((8-guessValue)/(8-fixValue))*100
    piPwm.ChangeDutyCycle(dc)
    time.sleep(0.1)

# Sound Buzzer
def trigger_buzzer():
    # The buzzer operates differently from the LED
    # While we want the brightness of the LED to change(duty cycle), we want the frequency of the buzzer to change
    # The buzzer duty cycle should be left at 50%
    # If the user is off by an absolute value of 3, the buzzer should sound once every second
    # If the user is off by an absolute value of 2, the buzzer should sound twice every second
    # If the user is off by an absolute value of 1, the buzzer should sound 4 times a second
    global piPwmBuzzer
    global guessValue
    global fixValue
    global name 
    global piPwm

    absValue = abs(guessValue - fixValue)\
    piPwmBuzzer.start(0)
    piPwmBuzzer.ChangeDutyCycle(0)
    start =  time.time()
    if( absValue == 0):
	print("Correct!")
	name = input("Enter name with 3 or more characters:\n")
	save_scores()
	piPmw = None
	piPwmBuzzer = None
	numberOfGuess = 0
	name = ""
	GPIO.remove_event_detect(btn_submit)
	GPIO.remove_event_detect(btn_increase)
	GPIO.output(LED_value[0],False)
	GPIO.output(LED_value[1],False)
	GPIO.output(LED_value[2],False)
	GPIO.output(buzzer,False)
	GPIO.cleanup()
	setup()
	welcome()
	while True:
		time.sleep(0.1)
		menu()
		pass
    if( absValue == 1):
        piPwmBuzzer.ChangeDutyCycle(50)
        while True:
                time.sleep(0.1)
                try:
                        piPwmBuzzer.ChangeFrequency(4)
                        time.sleep(0.1)
                        stop = time.time()
                        if(stop-start > 5):
                                piPwmBuzzer.stop()
                                break
                except Exception as e:
                        print("some error")
     if( absValue == 2):
        piPwmBuzzer.ChangeDutyCycle(50)
        while True:
                time.sleep(0.1)
                try:
                        piPwmBuzzer.ChangeFrequency(2)
                        time.sleep(0.1)
                        stop = time.time()
                        if(stop-start > 5):
                                piPwmBuzzer.stop()
                                break
                except Exception as e:
                        print("some error")
    if( absValue == 3):
	piPwmBuzzer.ChangeDutyCycle(50)
	while True:
		time.sleep(0.1)
		try:
			piPwmBuzzer.ChangeFrequency(1)
			time.sleep(0.1)
			stop = time.time()
			if(stop-start > 5):
				piPwmBuzzer.stop()
				break
		except Exception as e:
			print("some error")

    piPwmBuzzer.stop()
    time.sleep(0.1)

if __name__ == "__main__":
    try:
        # Call setup function
        setup()
        welcome()
        while True:
	    time.sleep(0.1)
            menu()
            pass
   except KeyboardInterrupt:
	print("Keyboard Interrupt")
    except Exception as e:
        print(e)
    finally:
	GPIO.output(LED_value[0],False)
	GPIO.output(LED_value[1],False)
	GPIO.output(LED_value[2],False)
	GPIO.output(buzzer,False)
	piPwm.stop()
        GPIO.cleanup()

