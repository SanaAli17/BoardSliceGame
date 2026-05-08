import tkinter as tk                     #GUI creation
from tkinter import messagebox, ttk      #message popups
from math import ceil, log2              #for optimal cut calculations
import time                              #tracking execution time
import winsound                          #sound effects

#helper function to add hover effect to buttons
def addHoverEffect(widget, normal, hover):
    widget.bind("<Enter>", lambda e: widget.config(bg=hover))
    widget.bind("<Leave>", lambda e: widget.config(bg=normal))

# Global States
m = n = 0                              #initial board dimensions                
current_m = current_n = 0              #current board dimenions - used in greedy
boards = []                            #list to store borads in D&C 
selected_index = -1                    #index of selected board - in manual D&C
cuts = 0                               
steps = []                             #list of steps for automatic greedy
start_time = 0
timer_running = False                  #boolean flag
game_finished = False                  #boolean flag
manual_mode = "V"                      #current mode horizontal/vertical

canvas_size = 360                     #fixed canvas size for board
cell_size = 40                        #default size of each cell

# WINDOW
root = tk.Tk()

# SCROLLABLE CONTAINER
#canvas used to enable vertical scrolling
main_canvas = tk.Canvas(root, bg="#1e1e2f", highlightthickness=0)

#scrollbar linked to canvas
scrollbar = tk.Scrollbar(root, orient="vertical", command=main_canvas.yview)

#frame inside canvas to hold UI elements
scroll_frame = tk.Frame(main_canvas, bg="#1e1e2f")

#updates the reigon whenever the content size changes
scroll_frame.bind(
    "<Configure>",
    lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
)

#places frmae inside canvas
main_canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

#connect scrollbar with canvas
main_canvas.configure(yscrollcommand=scrollbar.set)

#layout
main_canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# window config

root.withdraw()          #hide root temporaily to show menu first
root.title("Rectangular Board Cutting Game")
root.configure(bg="#1e1e2f")

# TITLE
# main frame
title_frame = tk.Frame(scroll_frame, bg="#1e1e2f")
title_frame.pack(pady=10)

#application title
tk.Label(
    title_frame,
    text=" BOARD CUTTING GAME",
    font=("Segoe UI", 24, "bold"),
    fg="#00cec9",
    bg="#1e1e2f"
).pack()

#subtitle
tk.Label(
    title_frame,
    text="Greedy vs Divide & Conquer Simulation",
    font=("Segoe UI", 11),
    fg="#a29bfe",
    bg="#1e1e2f"
).pack(pady=3)

# START SCREEN
def showMainMenu():
    
    #create window seperate
    menu = tk.Toplevel(root)
    menu.title("Main Menu")
    menu.geometry("300x250")
    menu.configure(bg="#1e1e2f")
    
    #title label
    tk.Label(menu, text=" Board Cutting Game",
             font=("Segoe UI", 14, "bold"),
             fg="#00cec9", bg="#1e1e2f").pack(pady=15)
    
    #buttons to start/get instructions/ exit
    tk.Button(menu, text="▶ Start Game", width=20,
              command=lambda: [menu.destroy(), showGame()],
              bg="#0984e3", fg="white").pack(pady=5)

    tk.Button(menu, text="📘 Instructions", width=20,
              command=showInstructions,
              bg="#6c5ce7", fg="white").pack(pady=5)

    tk.Button(menu, text="❌ Exit", width=20,
              command=root.destroy,
              bg="#d63031", fg="white").pack(pady=5)


def showInstructions():
    #display instructions on how to play
    
    messagebox.showinfo(
        "Instructions",
        "• Click on grid to cut\n"
        "• Choose Vertical or Horizontal mode\n"
        "• Goal: reach 1×1 with minimum cuts\n"
        "• Use Auto mode to see optimal solution"
    )

def showGame():
    root.deiconify()       #shows main window after menu
    #initial message
    messagebox.showinfo(
        "Game Ready",
        "Enter rows & columns\nChoose algorithm\nPress Start to begin"
    )

# main container for inputs
control_frame = tk.Frame(scroll_frame, bg="#1e1e2f")
control_frame.pack(pady=10)

# frame for user input
input_frame = tk.Frame(control_frame, bg="#2c2c54", bd=2, relief="ridge")
input_frame.pack(pady=15, padx=10)

# rows input label & entry
tk.Label(input_frame, text="Rows",
         font=("Segoe UI", 11, "bold"),
         fg="#00cec9",
         bg="#2c2c54").grid(row=0, column=0, padx=10, pady=10)

entry_m = tk.Entry(input_frame,
                   width=6,
                   justify="center",
                   font=("Segoe UI", 11),
                   bg="#dfe6e9",
                   fg="#2d3436",
                   bd=0)

#  default value for rows
entry_m.insert(0, "4")
entry_m.grid(row=0, column=1, padx=5)

# cols input label & entry
tk.Label(input_frame, text="Cols",
         font=("Segoe UI", 11, "bold"),
         fg="#55efc4",
         bg="#2c2c54").grid(row=0, column=2, padx=10)

entry_n = tk.Entry(input_frame,
                   width=6,
                   justify="center",
                   font=("Segoe UI", 11),
                   bg="#dfe6e9",
                   fg="#2d3436",
                   bd=0)

# default value for cols
entry_n.insert(0, "4")
entry_n.grid(row=0, column=3, padx=5)

# ALGORITHM SELECTION

# label
tk.Label(input_frame, text="Algorithm",
         font=("Segoe UI", 11, "bold"),
         fg="#fdcb6e",
         bg="#2c2c54").grid(row=0, column=4, padx=10)

algo_var = tk.StringVar()   # variable to store selected algo

# drop down menu for choosing algo
algo_menu = ttk.Combobox(
    input_frame,
    textvariable=algo_var,
    values=["Greedy", "Divide & Conquer"],
    state="readonly",
    width=18,
    justify="center"
)

# default algo set to greedy
algo_menu.set("Greedy")
algo_menu.grid(row=0, column=5, padx=10, pady=5)

# BUTTONS
# frame to hold start & reset buttons
btn_frame = tk.Frame(control_frame, bg="#1e1e2f")
btn_frame.pack(pady=5)

# start button
start_btn = tk.Button(btn_frame, text="Start", bg="#0984e3", fg="white",
                      width=10, command=lambda: start())
start_btn.grid(row=0, column=0, padx=5)

#reset button
reset_btn = tk.Button(btn_frame, text="Reset", bg="#d63031", fg="white",
                      width=10, command=lambda: resetGame())
reset_btn.grid(row=0, column=1, padx=5)

# hover effects through helper function
addHoverEffect(start_btn, "#0984e3", "#74b9ff")
addHoverEffect(reset_btn, "#d63031", "#ff7675")

# frame to hold manual mode buttons
manual_frame = tk.LabelFrame(control_frame, text="Manual Mode",
                             fg="white", bg="#1e1e2f")
manual_frame.pack(pady=5)

# displays current selected mode
mode_label = tk.Label(scroll_frame,
                      text="Current Mode: Vertical 🔽",
                      font=("Segoe UI", 10, "bold"),
                      fg="#00cec9",
                      bg="#1e1e2f")
mode_label.pack(pady=5)

# button for vertical cut
vertical_btn = tk.Button(manual_frame, text="Vertical Mode", bg="#00b894", fg="white",
                           width=12, command=lambda: manualAction("V"))
vertical_btn.grid(row=0, column=0, padx=10, pady=5)

#button for horizontal cut 
horizontal_btn = tk.Button(manual_frame, text="Horizontal Mode", bg="#00b894", fg="white",
                           width=12, command=lambda: manualAction("H"))
horizontal_btn.grid(row=0, column=1, padx=10, pady=5)

# hover effects through helper function
addHoverEffect(vertical_btn, "#00b894", "#55efc4")
addHoverEffect(horizontal_btn, "#00b894", "#55efc4")

# frame for Auto mode
auto_frame = tk.LabelFrame(control_frame, text="Auto Mode",
                           fg="white", bg="#1e1e2f")
auto_frame.pack(pady=5)

# button to start Automatic execution
auto_btn = tk.Button(auto_frame, text="Auto Start", bg="#fdcb6e", fg="black",
                     width=15, command=lambda: startAuto())
auto_btn.grid(row=0, column=0, padx=10, pady=5)

# hover effects through helper function
addHoverEffect(auto_btn, "#fdcb6e", "#ffeaa7")

# CANVAS
# main frame for drawing the grid
canvas = tk.Canvas(scroll_frame, bg="#2c2c54", highlightthickness=0)
canvas.pack()

# frame to display sub boards in D&C
boards_frame = tk.Frame(scroll_frame, bg="#1e1e2f")
boards_frame.pack(pady=10)

# label to display current info cuts/time/size
info = tk.Label(scroll_frame, fg="white", bg="#1e1e2f")
info.pack()

#timer label
timer_label = tk.Label(scroll_frame, text="Time: 0s", fg="white", bg="#1e1e2f")
timer_label.pack()

# SOUND
def playCutSound():
    winsound.Beep(800, 100)

def playWinSound():
    winsound.Beep(1200, 200)
    winsound.Beep(1500, 200)

# TIMER
def updateTimer():
    if timer_running:
        elapsed = round(time.time() - start_time, 1)
        timer_label.config(text=f"Time: {elapsed}s")
        root.after(100, updateTimer)   # refresh every 0.1 second

# GRID
# draw current board grid - used in greedy 
def drawGrid():
    canvas.delete("all")   # clear previous 
    global cell_size
    cell_size = canvas_size // max(m, n)  #adjust cell size dynamically
    
    #set canvas size based on current board
    canvas.config(width=current_n * cell_size,
                  height=current_m * cell_size)
    #draw grid cells
    for i in range(current_m):
        for j in range(current_n):
            x1 = j * cell_size
            y1 = i * cell_size
            x2 = x1 + cell_size
            y2 = y1 + cell_size
            canvas.create_rectangle(x1, y1, x2, y2,
                                    fill="#74b9ff", outline="#1e3799")
#draw orignal board used in D&C
def drawOriginalBoard():
    canvas.delete("all")   # clear previous
    
    #calculate cell based on board dimensions
    cell = canvas_size // max(m, n)
    
    #set canvas size to match orignal board
    canvas.config(
        width=n * cell,
        height=m * cell
    )
    #draw complete grid
    for i in range(m):
        for j in range(n):
            canvas.create_rectangle(
               j * cell, i * cell,
               (j + 1) * cell, (i + 1) * cell,
               fill="#636e72",
               outline="black"   
            )
            
# HOVER PREVIEW
preview_line = None        #to store preview line reference

def handleHover(event):
    
    if algo_var.get() == "Divide & Conquer":   # disbale giver in D&C mode
        return
    
    global preview_line

    if current_m == 0 or current_n == 0:     #ignore if board isnt initialized
        return
    
    #calculate grid position from mouse cordinates
    col = event.x // cell_size
    row = event.y // cell_size

    if preview_line:
        canvas.delete(preview_line)   #remove previous
    
    #show verticsl preview line
    if manual_mode == "V" and col < current_n:
        x = col * cell_size
        preview_line = canvas.create_line(x, 0, x, current_m * cell_size,
                                          fill="yellow", dash=(4, 2), width=2)
    #show horizontal preview line
    elif manual_mode == "H" and row < current_m:
        y = row * cell_size
        preview_line = canvas.create_line(0, y, current_n * cell_size, y,
                                          fill="yellow", dash=(4, 2), width=2)

# SPLIT PREVIEW
# Preview vertical split - highlights both sections
def previewSplitVertical(col):
    canvas.delete("split")   # remove previous
    x = col * cell_size

    canvas.create_rectangle(0, 0, x, current_m * cell_size,
                            fill="#55efc4", stipple="gray25", tags="split")
    canvas.create_rectangle(x, 0, current_n * cell_size, current_m * cell_size,
                            fill="#fab1a0", stipple="gray25", tags="split")
# Preview horizontal split
def previewSplitHorizontal(row):
    canvas.delete("split")
    y = row * cell_size

    canvas.create_rectangle(0, 0, current_n * cell_size, y,
                            fill="#55efc4", stipple="gray25", tags="split")
    canvas.create_rectangle(0, y, current_n * cell_size, current_m * cell_size,
                            fill="#fab1a0", stipple="gray25", tags="split")

# CLICK HANDLING
def handleClick(event):
    
    def handleClick(event):

    
     if algo_var.get() == "Divide & Conquer":   #disable in d&C mode
         return
     
    # get clicked cell position
    col = event.x // cell_size
    row = event.y // cell_size
    
    #perform vertical cut
    if manual_mode == "V" and current_n > 1 and col < current_n:
        previewSplitVertical(col)
        root.after(300, lambda: animateVertical(col,
            lambda: applyVertical(col, "Manual Vertical")))
        
    #perform horizontal cute
    elif manual_mode == "H" and current_m > 1 and row < current_m:
        previewSplitHorizontal(row)
        root.after(300, lambda: animateHorizontal(row,
            lambda: applyHorizontal(row, "Manual Horizontal")))
        
#bind mouse events to canvas
canvas.bind("<Motion>", handleHover)
canvas.bind("<Button-1>", handleClick)

# MODE SELECTION
# update manual cutting mode
def setMode(mode):
    global manual_mode
    manual_mode = mode
    
    #update ui for vertical
    if mode == "V":
        mode_label.config(text="Current Mode: Vertical 🔽")
        vertical_btn.config(bg="#00e676")
        horizontal_btn.config(bg="#00b894")
    #update ui for horizontal
    else:
        mode_label.config(text="Current Mode: Horizontal ➡")
        horizontal_btn.config(bg="#00e676")
        vertical_btn.config(bg="#00b894")
    #update info panel
    updateInfo(f"Mode: {'Vertical' if mode=='V' else 'Horizontal'}")

#handle manual button clicks    
def manualAction(mode):
    setMode(mode)

    if algo_var.get() == "Divide & Conquer":
        dcManualStep(mode)   #in D&C mode perform split on selected board
    
# CUT ANIMATION
# animate vertical cut line
def animateVertical(col, callback):
    x = col * cell_size
    line = canvas.create_line(x, 0, x, 0, fill="red", width=4)
    
    # gradually extend line downward
    def grow(y):
        if y <= current_m * cell_size:
            canvas.coords(line, x, 0, x, y)
            root.after(10, lambda: grow(y + 10))
        else:
            callback()    #apply cut after animation done
    grow(0)
    
#animate horizontal cut line
def animateHorizontal(row, callback):
    y = row * cell_size
    line = canvas.create_line(0, y, 0, y, fill="red", width=4)
    
    #gradually extend line sideways 
    def grow(x):
        if x <= current_n * cell_size:
            canvas.coords(line, 0, y, x, y)
            root.after(10, lambda: grow(x + 10))
        else:
            callback()   #appky cut after animation done
    grow(0)

# DISPLAY RESULT
def showResult():
    global timer_running, game_finished

    if game_finished:
        return         # to prevent multiple result popups

    game_finished = True
    timer_running = False
    
    #calculate total execution time
    total_time = round(time.time() - start_time, 2)
    
    #determine optimal cuts based on the algo selected
    if algo_var.get() == "Divide & Conquer":
       optimal = (m * n) - 1
    else:
       optimal = ceil(log2(m)) + ceil(log2(n))
    
    #evaluate result performance
    if cuts == optimal:
        result = "🏆 Perfect!"
    elif cuts == optimal + 1:
        result = "👍 Almost Optimal"
    else:
        result = "❌ Not Optimal"
    
    messagebox.showinfo("Game Result",
                    f"{result}\nCuts: {cuts}\nOptimal: {optimal}\nTime: {total_time}s")
    
    #ask user to replay or exit 
    again = messagebox.askyesno("Play Again", "Do you want to play again?")

    if again:
       resetGame()
    else:
       root.destroy()
    

# APPLY CUT - GREEDY LOGIC
def applyVertical(col, msg):
    global current_n, cuts
    current_n = max(col, current_n - col) #keep larger section after cut
    cuts += 1
    playCutSound()
    drawGrid()               # redraw updated grid
    updateInfo(msg)          # update info panel
    
    if current_m == 1 and current_n == 1:  # check if reduced to 1x1
        showResult()

def applyHorizontal(row, msg):
    global current_m, cuts
    current_m = max(row, current_m - row)   #keep larger section after cut
    cuts += 1
    playCutSound()
    drawGrid()                    # redraw updated grid
    updateInfo(msg)                # update info panel
    
    if current_m == 1 and current_n == 1:    # check if reduced to 1x1
        showResult()

 # draw sub boards D&C view
def drawBoards(board_list):
    global selected_index

    # clear previous boards
    for widget in boards_frame.winfo_children():
        widget.destroy()

    # determine size of mini boards - based in total count
    count = len(board_list)

    if count <= 8:
        size = 70
    elif count <= 16:
        size = 60
    elif count <= 32:
        size = 50
    else:
        size = 40

    max_per_row = 8   # layout control - 9 per row

    # draw each sub board
    for i, (r, c) in enumerate(board_list):

        mini = tk.Canvas(
            boards_frame,
            width=size,
            height=size,
            bg="#2c2c54",
            highlightthickness=2
        )

        # highlight the selected board
        if i == selected_index:
            mini.config(highlightbackground="yellow")
        else:
            mini.config(highlightbackground="white")

        # position board in the layout
        row = i // max_per_row
        col = i % max_per_row
        mini.grid(row=row, column=col, padx=5, pady=5)

        # calculate cell size inside the mini board
        cell = size // max(r, c)

        # draw grid of the sub board
        for x in range(r):
            for y in range(c):
                mini.create_rectangle(
                    y * cell, x * cell,
                    (y + 1) * cell, (x + 1) * cell,
                    fill="#74b9ff"
                )

        # display dimensions
        mini.create_text(
            size // 2,
            size // 2,
            text=f"{r}x{c}",
            fill="white",
            font=("Segoe UI", 8, "bold")
        )

        # bind click to select board
        mini.bind("<Button-1>", lambda e, idx=i: selectBoards(idx))
        
        main_canvas.yview_moveto(1)     #auto scroll to bottom
        
#board selection
def selectBoards(idx):
    global selected_index
    selected_index = idx       # store index of one slected 
    drawBoards(boards)         # refresh ui to highlight section

# generate all levels of D&C splitting
def generateDcLevels(m, n):
    levels = []
    current = [(m, n)]
    
    #continue spliiting until all boards reach 1x1
    while current:
        levels.append(current)
        next_level = []

        for r, c in current:
            if r == 1 and c == 1:  # skip if already smallest unit
                continue
            
            # split vertically if possible
            if c > 1:
                next_level.append((r, c//2))
                next_level.append((r, (c+1)//2))
            # split horizontally otherwise
            elif r > 1:
                next_level.append((r//2, c))
                next_level.append(((r+1)//2, c))

        current = next_level

    return levels

# animate D&C splitting level by level
def showDcTree():
    levels = generateDcLevels(m, n)  #generate all split levels
    
    #display each level with animation
    def show_level(i):
        if i >= len(levels):
            return

        drawBoards(levels[i])   #draw current level 
        root.after(800, lambda: show_level(i+1)) # move to next level

    show_level(0)   #start animation

    
# D&C Auto step 
# perform one step of D&C splitting 
def dcStep():
    global boards, cuts

    new_boards = []

    for r, c in boards:
        
        #keep board if already 1x1
        if r == 1 and c == 1:
            new_boards.append((r, c))
            continue
        
        #split vertically
        if c > 1:
            left = (r, c // 2)
            right = (r, (c + 1) // 2)
            new_boards.extend([left, right])
            cuts += 1
        
        # split horizontally 
        elif r > 1:
            top = (r // 2, c)
            bottom = ((r + 1) // 2, c)
            new_boards.extend([top, bottom])
            cuts += 1

    boards = new_boards     #update board list after split 

# D&C MANUAL STEP
#perform user controlled split on selected board
def dcManualStep(mode):
    global boards, selected_index, cuts
    #ensure board is selected
    if selected_index == -1:
        messagebox.showwarning("Select Board", "Click a board first!")
        return

    r, c = boards[selected_index]

    # remove selected board before splitting
    boards.pop(selected_index)

    # apply user selected split direction
    if mode == "V":
        if c > 1:
            boards.append((r, c // 2))
            boards.append((r, (c + 1) // 2))
            cuts += 1
        else:
            messagebox.showwarning("Invalid Cut", "Cannot cut vertically!")
            boards.insert(selected_index, (r, c))
            return

    elif mode == "H":
        if r > 1:
            boards.append((r // 2, c))
            boards.append(((r + 1) // 2, c))
            cuts += 1
        else:
            messagebox.showwarning("Invalid Cut", "Cannot cut horizontally!")
            boards.insert(selected_index, (r, c))
            return

    selected_index = -1    # reset selection after split
    
    # update UI and info panel
    drawBoards(boards)
    updateInfo(f"Manual D&C {'Vertical' if mode=='V' else 'Horizontal'}")
    
    #check all reduced to 1x1
    if all(r == 1 and c == 1 for r, c in boards):
        showResult()

# run selected algo automatically 
def autoRun():
    
    # D&C mode
    if algo_var.get() == "Divide & Conquer":

        if all(r == 1 and c == 1 for r, c in boards):
            showResult()
            return

        dcStep()                   #perform one D&C split
        drawBoards(boards)         #update board display
        updateInfo("D&C Splitting...")
        
        #auto scroll to show latest boards
        root.after(50, lambda: main_canvas.yview_moveto(1))
        
        root.after(800, autoRun) #continue next step after delay

    # greedy mode
    else:
        # stop when no steps left
        if not steps:
            showResult()
            return

        step = steps.pop(0)   #get next step
        
        # execute with animation
        if step[0] == "V":
            animateVertical(step[1],
                lambda: applyVertical(step[1], step[2]))
        else:
            animateHorizontal(step[1],
                lambda: applyHorizontal(step[1], step[2]))

        root.after(900, autoRun)  #continue next step after delay
        
# AUTO START MODE
 # Initialize and runs the selected algo   
def startAuto():
    global steps, cuts, m, n, current_m, current_n, start_time, timer_running, game_finished, boards

    game_finished = False

    # input validation
    try:
        m = int(entry_m.get())
        n = int(entry_n.get())

        if m <= 0 or n <= 0:
            raise ValueError

        if m > 20 or n > 20:    # limit board for UI performance
            messagebox.showwarning("Limit Exceeded", "Max allowed size is 20 x 20")
            return

    except:
        messagebox.showerror("Invalid Input", "Enter positive integers only")
        return

    cuts = 0

    # divide and conquer
    if algo_var.get() == "Divide & Conquer":

        boards = [(m, n)]  #initialize with orignal board

        drawOriginalBoard()     # display full board
        drawBoards(boards)      #display first level

        # reset scroll position to top 
        main_canvas.yview_moveto(0)

    # greedy 
    else:
        current_m, current_n = m, n
        drawGrid()

    messagebox.showinfo("Auto Mode", f"{algo_var.get()} Running") # notify yser
   
    start_time = time.time()    # start timer 
    timer_running = True
    updateTimer()

    # algo execution
    if algo_var.get() == "Greedy":
        steps = generateGreedy()       # generate sequence of cuts 
        autoRun()

    else:
        autoRun()             # run D&C directly

# ALGORITHMS

# recursively calculate total cuts using D&C
def divideConquerCount(m, n):
    
    if m == 1 and n == 1:
        return 0            # no more cuts needed
    
    #prefer vertical split
    if n > 1:
        return (1 +
                divideConquerCount(m, n // 2) +
                divideConquerCount(m, (n + 1) // 2))
    
    #else horizontal split
    elif m > 1:
        return (1 +
                divideConquerCount(m // 2, n) +
                divideConquerCount((m + 1) // 2, n))
    
# steps for greedy algo - largest side split first 
def generateGreedy():
    
    r, c = m, n
    s = []
    
    while not (r == 1 and c == 1):
        # split larger dimension
        if c >= r:
            s.append(("V", c // 2, "Greedy"))
            c = ceil(c / 2)
        else:
            s.append(("H", r // 2, "Greedy"))
            r = ceil(r / 2)
    return s

# simplified D&C step for auto run
def generateDc():
    
    s = []
    c = n
    
    #vertical splits
    while c > 1:
        s.append(("V", c // 2, "D&C"))
        c = ceil(c / 2)
        
    # horizontal splits
    r = m
    while r > 1:
        s.append(("H", r // 2, "D&C"))
        r = ceil(r / 2)

    return s

# START GAME
#initialize game in manual mode
def start():
    global m, n, current_m, current_n, cuts, start_time, timer_running, game_finished, boards, selected_index

    game_finished = False

    # input validation
    try:
        m = int(entry_m.get())
        n = int(entry_n.get())

        if m <= 0 or n <= 0:
            raise ValueError

        if m > 20 or n > 20:
            messagebox.showwarning("Limit Exceeded", "Max allowed size is 20 x 20")
            return

    except:
        messagebox.showerror("Invalid Input", "Enter positive integers only")
        return

    # reset state
    cuts = 0
    boards.clear()
    selected_index = -1
    
    # clear canvas for greedy mode
    if algo_var.get() == "Greedy":
       canvas.delete("all")

    # mode handling
    
    if algo_var.get() == "Divide & Conquer":

        boards = [(m, n)]      #initial board
        
        drawOriginalBoard()    #show full grid
        drawBoards(boards)     #show sub board view
 
        messagebox.showinfo(
            "Game Started",
            f"D&C Mode\n{m} x {n}\nClick a board to select, then press a button to split"
        )

    else:
        current_m, current_n = m, n
        drawGrid()      #draw grid for greedy mode
        
        messagebox.showinfo("Game Started", f"{m} x {n}")

    # timer
    start_time = time.time()
    timer_running = True
    updateTimer()

# reset game state and UI
def resetGame():
    
    global cuts, steps, current_m, current_n, timer_running, game_finished
    
    timer_running = False
    game_finished = False
    cuts = 0
    steps = []
    current_m = current_n = 0
    canvas.delete("all")        # clear main grid
    boards.clear()              #clear D&C boards
    drawBoards([])              # refresh empty board view
    
    # Redraw original board if in D&C mode
    if algo_var.get() == "Divide & Conquer" and m > 0 and n > 0:
        drawOriginalBoard()
        
    # Reset UI labels 
    timer_label.config(text="Time: 0s")
    info.config(text="Game Reset")

# Update information panel with current status
def updateInfo(msg):
    
    # D&C Display
    if algo_var.get() == "Divide & Conquer":
        optimal = (m * n) - 1

        # show no of sub boards
        size_text = f"{len(boards)} boards"

        # optionally show selected board size
        if 'selected_index' in globals() and selected_index != -1 and selected_index < len(boards):
            r, c = boards[selected_index]
            size_text += f" (Selected: {r} x {c})"
            
    #greedy display
    else:
        optimal = ceil(log2(m)) + ceil(log2(n))
        size_text = f"{current_m} x {current_n}"
        
    #update info label
    info.config(
        text=f"{msg}\nSize: {size_text}\nCuts: {cuts}\nOptimal: {optimal}"
    )

showMainMenu()
root.mainloop()