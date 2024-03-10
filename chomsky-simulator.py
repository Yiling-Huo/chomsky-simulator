import pygame, gensim, csv, os, sys, random, numpy

##########
# Appearances
##########
window_width = 1400
window_height = 900

porcelain = '#fdfdfd'
jet = '#353535'
french = '#D2D7DF'
silver = '#BDBBB0'
battleship = '#8A897C'

##########
# Classes
##########
# button code from:
# https://pythonprogramming.sssaltervista.org/buttons-in-pygame/?doing_wp_cron=1685564739.9689290523529052734375
class Button:
    def __init__(self,text,width,height,pos,elevation,onclickFunction=None):
        #Core attributes 
        self.pressed = False
        self.onclickFunction = onclickFunction
        self.elevation = elevation
        self.dynamic_elecation = elevation
        self.original_y_pos = pos[1]

        # top rectangle 
        self.top_rect = pygame.Rect(pos,(width,height))
        self.top_color = battleship

        # bottom rectangle 
        self.bottom_rect = pygame.Rect(pos,(width,height))
        self.bottom_color = jet
        #text
        self.text = text
        self.text_surf = button_font.render(text,True,'#FFFFFF')
        self.text_rect = self.text_surf.get_rect(center = self.top_rect.center)

    def draw(self):
        # elevation logic 
        self.top_rect.y = self.original_y_pos - self.dynamic_elecation
        self.text_rect.center = self.top_rect.center 

        self.bottom_rect.midtop = self.top_rect.midtop
        self.bottom_rect.height = self.top_rect.height + self.dynamic_elecation

        pygame.draw.rect(screen,self.bottom_color, self.bottom_rect,border_radius = 12)
        pygame.draw.rect(screen,self.top_color, self.top_rect,border_radius = 12)
        screen.blit(self.text_surf, self.text_rect)
        self.check_click()

    def check_click(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.top_rect.collidepoint(mouse_pos):
            self.top_color = silver
            if pygame.mouse.get_pressed()[0]:
                self.dynamic_elecation = 0
                self.pressed = True
            else:
                self.dynamic_elecation = self.elevation
                if self.pressed == True:
                    self.onclickFunction()
                    self.pressed = False
        else:
            self.dynamic_elecation = self.elevation
            self.top_color = battleship


class Text_button:
    def __init__(self,text,pos,onclickFunction=None):
        #Core attributes 
        self.pressed = False
        self.onclickFunction = onclickFunction
        self.pos = pos

        self.text = text
        self.text_color = battleship
        self.text_surf = button_font.render(text,True,self.text_color)
        self.text_rect = self.text_surf.get_rect(topleft = pos)

    def draw(self):
        pygame.draw.rect(screen,porcelain,pygame.Rect(self.pos,(300,60)),border_radius = 3)
        self.text_surf = button_font.render(self.text,True,self.text_color)
        screen.blit(self.text_surf, self.text_rect)
        self.check_click()

    def check_click(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.text_rect.collidepoint(mouse_pos):
            self.text_color = jet
            if pygame.mouse.get_pressed()[0]:
                self.pressed = True
            else:
                if self.pressed == True:
                    self.onclickFunction()
                    self.pressed = False
        else:
            self.text_color = battleship

########
# Functions
########

# load word2vec model
def load_sim_model():
    sim_model = gensim.models.KeyedVectors.load_word2vec_format('assets/glove-wiki-gigaword-200.txt', binary=False)
    return sim_model

# roll text (for intro)
def roll_text(text, x, y, delay=100):
    for i in range(len(text)):
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        # Render the text up to the current character
        rendered_text = text_font.render(text[:i + 1], True, jet)
        text_rect = rendered_text.get_rect(center=(x, y))
        # Clear the area
        pygame.draw.rect(screen,porcelain,text_rect,border_radius = 3)
        # Blit the rendered text onto the screen
        screen.blit(rendered_text, text_rect)
        # Update the display
        pygame.display.flip()
        # Introduce a delay between characters
        pygame.time.delay(delay)

# wipe screen
def wipe():
    pygame.draw.rect(screen, porcelain, pygame.Rect(0, 0, window_width, window_height))
    pygame.display.flip()

# onclickfunctions for the start button
def start():
    global started, hard, start_button, start_button_hard
    started = True
    hard = False
    wipe()
    init_game()

def start_hard():
    global started, hard
    started = True
    hard = True
    wipe()
    init_game()

# initialise a game of 20 trials
def init_game():
    global trial_count, correct_count, reached_end, chomsky_score
    wipe()
    trial_count = 0
    correct_count = 0
    chomsky_score = 0
    reached_end = False
    init_trial()

# initialise a trial
def init_trial():
    global trial_count, sentence, selected, current_location, last_content_word, stepwise_score, trial_score
    wipe()
    sentence = []
    trial_score = 0
    generate(cfg)
    # change variables
    selected = [[random.choice(words[sentence[0]])]]
    if sentence[0][0] in content_words:
        last_content_word = selected[0][0]
    else:
        last_content_word = ''
    # the first word doesn't count into the scores
    stepwise_score = int(100/(len(sentence)-1))
    current_location = 1
    get_options(sentence, current_location, stepwise_score)

# generate a sentence skeleton such as [node, node, node]
def generate(cfg, node='S'):
    global sentence
    expansion = random.choice(cfg[node])
    # expansion is a list of sub nodes, with elements either being the name of terminal or not
    for n in expansion:
        # if non-terminal node (it should exist as a key in cfg)
        if n in cfg:
            generate(cfg, n) 
        # if terminal node
        else:
            sentence.append(n)

def get_options(sentence, current_location, stepwise_score):
    global options, options_text, option_buttons
    options = {}
    # if a content word, get one ungrammatical and two grammatical options
    if sentence[current_location] in content_words:
        # get one ungrammatical option
        ungrammatical_node = random.choice([key for key in list(words.keys()) if key not in block_list[sentence[current_location]]])
        ungrammatical_choice = random.choice(words[ungrammatical_node])
        # ungrammatical choice will reduce chomsky_score by stepwise
        options[ungrammatical_choice] = -stepwise_score
        # get two grammatical options and give them scores based on similarity
        options.update(get_options_based_on_similarity(sentence, current_location, stepwise_score))
    # if not a content word, get two ungrammatical and one grammatical option
    else:
        options.update(get_two_ungrammatics(sentence, current_location, stepwise_score))
    # scramble the order of correct/incorrect options and get button objects
    options_text = list(options.keys())
    random.shuffle(options_text)
    option_buttons = [Text_button(option, (150, 400+(options_text.index(option)*80)), select) for option in options_text]

def get_options_based_on_similarity(sentence, current_location, stepwise_score):
    options = {}
    # get two grammatical options
    option1 = random.choice(words[sentence[current_location]])
    second_pool = words[sentence[current_location]].copy()
    second_pool.remove(option1)
    option2 = random.choice(second_pool)
    if len(last_content_word) > 0:
        try:
            # calculate scores for each options based on similarity
            similarity1 = sim_model.similarity(option1, last_content_word)
            similarity2 = sim_model.similarity(option2, last_content_word)
            if similarity1 > similarity2:
                options[option2] = stepwise_score
                options[option1] = int((stepwise_score/2))
            elif similarity1 < similarity2:
                options[option1] = stepwise_score
                options[option2] = int((stepwise_score/2))
            else:
                options[option1] = stepwise_score
                options[option2] = stepwise_score
        except KeyError:
            return get_options_based_on_similarity(sentence, current_location, stepwise_score)
    else:
        # if this is the first content word, just consider both options the best one
        options[option1] = stepwise_score
        options[option2] = stepwise_score
    return options

def get_two_ungrammatics(sentence, current_location, stepwise_score):
    options = {}
    # get ungrammatical options
    ungrammatical_node1 = random.choice([key for key in list(words.keys()) if key not in block_list[sentence[current_location]]])
    ungrammatical_choice1 = random.choice(words[ungrammatical_node1])
    ungrammatical_node2 = random.choice([key for key in list(words.keys()) if key not in block_list[sentence[current_location]]])
    if ungrammatical_node1 == ungrammatical_node2:
        second_pool = words[ungrammatical_node2].copy()
        second_pool.remove(ungrammatical_choice1)
        try:
            ungrammatical_choice2 = random.choice(second_pool)
        except IndexError:
            return get_two_ungrammatics(sentence, current_location, stepwise_score)
    else:
        ungrammatical_choice2 = random.choice(words[ungrammatical_node2])
    # ungrammatical choice will reduce chomsky_score by stepwise
    options[ungrammatical_choice1] = -stepwise_score
    options[ungrammatical_choice2] = -stepwise_score
    # get one grammatical option
    option = random.choice(words[sentence[current_location]])
    options[option] = stepwise_score
    return options

def select():
    global chomsky_score, trial_score, last_content_word, option_buttons
    mouse_pos = pygame.mouse.get_pos()
    answer = ''
    for button in option_buttons:
        if button.text_rect.collidepoint(mouse_pos):
            answer = options_text[option_buttons.index(button)]
    if len(answer) == 0:
        return
    # show score change for a while
    start_time = pygame.time.get_ticks()
    delay = 750
    while True:
        current_time = pygame.time.get_ticks()
        # repeat what's done in main loop to prevent freezing
        for i in range(len(selected)):
            message = text_font.render(' '.join(selected[i]), True, jet)
            screen.blit(message, message.get_rect(topleft = (95, 150+(i*50))))
        score = text_font_small.render('Chomsky score: '+str(chomsky_score), True, jet)
        screen.blit(score, score.get_rect(topleft = (900, 75)))
        # print message
        message = text_font_small.render('+'+str(options[answer]) if options[answer] > 0 else str(options[answer]), True, jet)
        screen.blit(message, message.get_rect(center = (825, 75)))
        pygame.display.flip()
        if current_time - start_time >= delay:
            break
    trial_score += options[answer]
    chomsky_score += options[answer]
    if options[answer] > 0:
        last_content_word = answer
        selected[-1].append(answer) if len(selected[-1]) < 7 else selected.append([answer])
        correct()
    else:
        wrong()
    wipe()

def correct():
    global sentence, current_location, stepwise_score, trial_count
    # if end of sentence, start a new trial
    if current_location == len(sentence)-1:
        trial_count += 1
        # initialise another trial after some time
        correct = button_font.render('Cool!', True, jet) if trial_score > 80 else button_font.render('Nice!', True, jet)
        start_time = pygame.time.get_ticks()
        delay = 750
        while True:
            current_time = pygame.time.get_ticks()
            # repeat what's done in main loop to prevent freezing
            for i in range(len(selected)):
                if i == len(selected)-1:
                    message = text_font.render(' '.join(selected[i])+'.', True, jet)
                else:
                    message = text_font.render(' '.join(selected[i]), True, jet)
                screen.blit(message, message.get_rect(topleft = (95, 150+(i*50))))
            score = text_font_small.render('Chomsky score: '+str(chomsky_score), True, jet)
            screen.blit(score, score.get_rect(topleft = (900, 75)))
            # print correct message
            screen.blit(correct, correct.get_rect(center = (700, 340)))
            pygame.display.flip()
            if current_time - start_time >= delay:
                init_trial()
                break
    else:
        pygame.display.flip()
        current_location += 1
        get_options(sentence, current_location, stepwise_score)

def wrong():
    global trial_count
    trial_count += 1
    start_time = pygame.time.get_ticks()
    delay = 1000
    while True:
        current_time = pygame.time.get_ticks()
        # repeat what's done in main loop to prevent freezing
        for i in range(len(selected)):
            message = text_font.render(' '.join(selected[i]), True, jet)
            screen.blit(message, message.get_rect(topleft = (95, 150+(i*50))))
        score = text_font_small.render('Chomsky score: '+str(chomsky_score), True, jet)
        screen.blit(score, score.get_rect(topleft = (900, 75)))
        # print wrong message
        wrong = button_font.render('Oh no, ungrammatical...', True, jet)
        screen.blit(wrong, wrong.get_rect(center = (700, 340)))
        pygame.display.flip()
        if current_time - start_time >= delay:
            init_trial()
            break

def quit():
    global running
    running = False

##########
# Main game
##########
def main():
    global screen, icon, clock, button_font, text_font, text_font_small, button_font_tr, text_font_tr
    global cfg, content_words, words, block_list, sim_model
    global running, started, hard, selected, current_location, option_buttons, option_1_rect, option_2_rect, option_3_rect
    # Set working directory to the location of this .py file
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    pygame.init()
    screen = pygame.display.set_mode((window_width, window_height))
    clock = pygame.time.Clock()
    icon = pygame.image.load('assets/icon.png')
    pygame.display.set_icon(icon)
    pygame.display.set_caption('Chomsky Simulator')
    screen.fill(porcelain)
    text_font_small = pygame.font.Font('assets/joystix-monospace.otf',20)
    text_font = pygame.font.Font('assets/joystix-monospace.otf',24)
    button_font = pygame.font.Font('assets/joystix-monospace.otf',28)

    # roll intro
    roll_text('Colorless green ideas sleep furiously.', 700, 400)
    pygame.time.delay(300)
    roll_text('- Noam Chomsky', 900, 600)
    pygame.time.delay(1000)

    # game variables
    started = False

    # get materials
    wipe()
    load_message = text_font.render('Loading NLP magic...', True, jet)
    screen.blit(load_message, load_message.get_rect(center = (950, 750)))
    pygame.display.flip()

    # get cfg from a .csv file of either node,word or node,node1,node2
    with open('assets/cfg.csv', 'r') as inputfile:
        cr = csv.reader(inputfile)
        content = [line for line in cr if len(line)>0]
        cfg = {}
        for row in content:
            try:
                cfg[row[0]].append(row[1:])
            except KeyError:
                cfg[row[0]] = [row[1:]]
    # get a pos:words dictionary
    needed = ['NN','NNS','DTS','DTP','JJ','CD','VBDI','VBZI','VBGI','RBA','VBD','VBZ','VBG','COPSN','COPSP','VBI','VB','COPPN','COPPP','RBP','IN']
    content_words = ['NN','NNS','JJ','VBDI','VBZI','VBGI','RBA','VBD','VBZ','VBG','VBI','VB','RBP']
    with open('assets/pos_corpus_built_from_wiki_cleaned.csv', 'r') as wordinput:
        cr = csv.reader(wordinput)
        words = {}
        for line in cr:
            if line[0] in needed:
                if line[0] not in words:
                    words[line[0]] = [line[1]]
                else:
                    words[line[0]].append(line[1])
    # get the block list
    with open('assets/block_list.csv', 'r') as blockinput:
        cr = csv.reader(blockinput)
        block_list = {}
        for line in cr:
            block_list[line[0]] = line[1:]
    # load similarity model
    sim_model = load_sim_model()

    # game assets
    start_button = Button('start', 130, 50, (535, 400), 3, start)
    quit_button = Button('quit game', 220, 50, (490, 500), 3, quit)
    chat = pygame.transform.scale(pygame.image.load('assets/chat2.png'), (200,200))
    idea_dark = pygame.transform.scale(pygame.image.load('assets/idea-dark.png'), (350,350))
    idea_light = pygame.transform.scale(pygame.image.load('assets/idea-light.png'), (350,350))
    ideas = [idea_dark, idea_light]
    index = 0
    interval = 2500
    start_time = pygame.time.get_ticks()

    # get ready to start
    wipe()
    running = True

    # main loop
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                # pygame.quit()
        
        # draw the lightbulb and the chat images
        screen.blit(chat, (800,400))
        current_time = pygame.time.get_ticks()
        screen.blit(ideas[index], (1000,475))
        if current_time - start_time >= interval:
            pygame.draw.rect(screen,porcelain,pygame.Rect(1000, 475, 350, 350))
            if index == 1:
                index -= 1
            else:
                index += 1
            start_time = current_time
        pygame.display.flip()

        # manage game
        if not started:
            message1 = text_font.render('Welcome to Chomsky Simulator!', True, jet)
            message2 = text_font_small.render("Let's build grammatical sentences that make no semantic sense.", True, jet)
            message3 = text_font_small.render('Select the option that best continues the sentence in a Chomskian way.', True, jet)
            screen.blit(message1, message1.get_rect(center = (600, 100)))
            screen.blit(message2, message2.get_rect(topleft = (100, 200)))
            screen.blit(message3, message3.get_rect(topleft = (100, 250)))
            start_button.draw()
        elif trial_count == 10:
            # only cover the area that's not the lightbulbs
            pygame.draw.rect(screen, porcelain, pygame.Rect(0, 0, window_width, 395))
            pygame.draw.rect(screen, porcelain, pygame.Rect(0, 0, 795, window_height))
            message1 = text_font.render('Game end!', True, jet)
            message2 = text_font_small.render('Your Chomsky score: '+str(chomsky_score), True, jet)
            message3 = text_font_small.render('Another game?', True, jet)
            screen.blit(message1, message1.get_rect(center = (600, 150)))
            screen.blit(message2, message2.get_rect(center = (600, 200)))
            screen.blit(message3, message3.get_rect(center = (600, 270)))
            start_button.draw()
            quit_button.draw()
        else:
            for i in range(len(selected)):
                message = text_font.render(' '.join(selected[i]), True, jet)
                screen.blit(message, message.get_rect(topleft = (95, 150+(i*50))))
            score = text_font_small.render('Chomsky score: '+str(chomsky_score), True, jet)
            screen.blit(score, score.get_rect(topleft = (900, 75)))
            for option in option_buttons:
                option.draw()
        pygame.display.flip()
        clock.tick(60)

    # quit game
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()