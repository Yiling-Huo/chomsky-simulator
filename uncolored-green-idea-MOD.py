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
    sim_model = gensim.models.KeyedVectors.load_word2vec_format('assets/data/glove-wiki-gigaword-200.txt', binary=False)
    return sim_model

# roll text (for intro and debrief)
def roll_text(text, x, y, delay=100, font=''):
    for i in range(len(text)):
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        if font == 'small':
            # Render the text up to the current character
            rendered_text = text_font_smaller.render(text[:i + 1], True, jet)
            # because this is only used or debriefing so can simply use topleft
            text_rect = rendered_text.get_rect(topleft=(x, y))
        elif font == 'large':
            # Render the text up to the current character
            rendered_text = text_font_large.render(text[:i + 1], True, jet)
            text_rect = rendered_text.get_rect(center=(x, y))
        else:
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

# onClickFunction for the quit button
def quit():
    global running
    running = False

# onClickFunction for the start button
def start():
    global debriefing, started
    debriefing = False
    started = True
    wipe()
    init_game()

# initialise a game of 10 trials
def init_game():
    global trial_count, correct_count, chomsky_score, all_sentences, rolling
    wipe()
    trial_count = 0
    correct_count = 0
    chomsky_score = 0
    all_sentences = []
    rolling = True
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
        ungrammatical_node = random.choice([key for key in list(words.keys()) if key in white_list[sentence[current_location]]])
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
    ungrammatical_node1 = random.choice([key for key in list(words.keys()) if key in white_list[sentence[current_location]]])
    ungrammatical_choice1 = random.choice(words[ungrammatical_node1])
    ungrammatical_node2 = random.choice([key for key in list(words.keys()) if key in white_list[sentence[current_location]]])
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
        score = text_font.render('CP: '+str(chomsky_score), True, jet)
        screen.blit(score, score.get_rect(topleft = (1050, 75)))
        # print message
        message = text_font_small.render('+'+str(options[answer]) if options[answer] > 0 else str(options[answer]), True, jet)
        screen.blit(message, message.get_rect(center = (950, 75)))
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
            score = text_font.render('CP: '+str(chomsky_score), True, jet)
            screen.blit(score, score.get_rect(topleft = (1050, 75)))
            # print correct message
            screen.blit(correct, correct.get_rect(center = (700, 340)))
            pygame.display.flip()
            if current_time - start_time >= delay:
                break
        # add the sentence to all sentences
        selected[-1][-1] += '.'
        all_sentences.append([' '])
        for line in selected:
            all_sentences.append(line)
        wipe()
        init_trial()
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
        score = text_font.render('CP: '+str(chomsky_score), True, jet)
        screen.blit(score, score.get_rect(topleft = (1050, 75)))
        # print wrong message
        wrong = button_font.render('Oh no, ungrammatical...', True, jet)
        screen.blit(wrong, wrong.get_rect(center = (700, 340)))
        pygame.display.flip()
        if current_time - start_time >= delay:
            break
    # add the sentence to all sentences
    all_sentences.append([' '])
    for line in selected:
        all_sentences.append(line)
    wipe()
    init_trial()

def roll_all_sentences():
    global rolling
    if rolling:
        for i in range(len(all_sentences)):
            roll_text(' '.join(all_sentences[i]), 100, 100+(i*25),delay=35,font='small')
            rolling = False
    else:
        for i in range(len(all_sentences)):
            message = text_font_smaller.render(' '.join(all_sentences[i]), True, jet)
            screen.blit(message, message.get_rect(topleft = (100, 100+(i*25))))

##########
# Main function
##########
def main():
    global screen, icon, clock, button_font, text_font, text_font_large, text_font_small, text_font_smaller
    global cfg, content_words, words, white_list, sim_model
    global running, started, selected, current_location, option_buttons
    ##########
    # Initialise
    ##########
    # Set working directory to the location of this .py file
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((window_width, window_height))
    clock = pygame.time.Clock()
    icon = pygame.image.load('assets/aes/icon.png')
    pygame.display.set_icon(icon)
    pygame.display.set_caption('Uncolored Green Idea Game')
    screen.fill(porcelain)

    ##########
    # Game assets
    ##########
    # text fonts
    text_font_smaller = pygame.font.Font('assets/aes/joystix-monospace.otf',15)
    text_font_small = pygame.font.Font('assets/aes/joystix-monospace.otf',20)
    text_font = pygame.font.Font('assets/aes/joystix-monospace.otf',24)
    text_font_large = pygame.font.Font('assets/aes/joystix-monospace.otf',50)
    button_font = pygame.font.Font('assets/aes/joystix-monospace.otf',28)
    # buttons
    start_button = Button('start', 130, 50, (535, 550), 3, start)
    restart_button = Button('new game', 220, 50, (800, 300), 3, start)
    quit_button = Button('quit game', 220, 50, (1100, 300), 3, quit)
    # the green idea
    chat = pygame.transform.scale(pygame.image.load('assets/aes/chat2.png'), (200,200))
    idea_dark = pygame.transform.scale(pygame.image.load('assets/aes/idea-dark.png'), (350,350))
    idea_light = pygame.transform.scale(pygame.image.load('assets/aes/idea-light.png'), (350,350))
    ideas = [idea_dark, idea_light]
    index = 0
    interval = 2500

    ##########
    # Roll Intro
    ##########
    roll_text('Colorless green ideas sleep furiously.', 700, 400)
    pygame.time.delay(300)
    roll_text('- Noam Chomsky', 900, 600)
    pygame.time.delay(750)
    wipe()
    pygame.time.delay(500)
    roll_text('uncolored green idea game', 700, 400, delay=150,font='large')
    pygame.time.delay(1250)

    ##########
    # Get matrials
    ##########
    # play loading bgm
    pygame.mixer_music.load('assets/aes/maou_bgm_8bit2.mp3')
    pygame.mixer.music.play(-1,0.0)
    # show message
    wipe()
    load_message = text_font.render('Loading NLP magic...', True, jet)
    screen.blit(load_message, load_message.get_rect(center = (950, 750)))
    pygame.display.flip()

    # get cfg from a .csv file of either node,word or node,node1,node2
    with open('assets/data/cfg.csv', 'r') as inputfile:
        cr = csv.reader(inputfile)
        content = [line for line in cr if len(line)>0]
        cfg = {}
        for row in content:
            try:
                cfg[row[0]].append(row[1:])
            except KeyError:
                cfg[row[0]] = [row[1:]]
    # get a pos:words dictionary
    # I removded all the irregular past particles and just used VBN as the past tense verb
    needed = ['NN','NNS','DTS','DTP','JJ','CD','VBDI','VBZI','VBGI','RBA','VBD','VBN','VBZ','VBG','COPSN','COPSP','VBI','VB','VBP','COPPN','COPPP','RBP','IN']
    content_words = ['NN','NNS','JJ','VBDI','VBZI','VBGI','RBA','VBD','VBN','VBZ','VBG','VBI','VB','VBP','RBP']
    with open('assets/data/pos_corpus_built_from_wiki_cleaned.csv', 'r') as wordinput:
        cr = csv.reader(wordinput)
        words = {}
        for line in cr:
            if line[0] in needed:
                if line[0] not in words:
                    words[line[0]] = [line[1]]
                else:
                    words[line[0]].append(line[1])
    # get the white list for ungrammatical choices
    with open('assets/data/incorrect_continuations.csv', 'r') as blockinput:
        cr = csv.reader(blockinput)
        white_list = {}
        for line in cr:
            white_list[line[0]] = line[1:]
    # load similarity model
    sim_model = load_sim_model()
    # sim_model = []

    ##########
    # Main game logic
    ##########
    # switch bgm
    pygame.mixer.music.stop()
    pygame.mixer_music.load('assets/aes/maou_bgm_8bit16.mp3')
    pygame.mixer.music.play(-1,0.0)
    # get ready to start
    wipe()
    start_time = pygame.time.get_ticks()
    started = False
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
            message1 = text_font.render('Uncolored Green Idea Game', True, jet)
            message2 = text_font_small.render("Let's build grammatical sentences that make no semantic sense.", True, jet)
            message3 = text_font_small.render('Choose the option that continues the sentence grammatically.', True, jet)
            message4 = text_font_small.render('Gain more C(homsky)P(oints) if your choice makes less sense.', True, jet)
            message5 = text_font_small.render('created by Yiling Huo', True, battleship)
            message6 = text_font_smaller.render('images: Bakunetsu Kaito', True, battleship)
            message7 = text_font_smaller.render('music: maoudamashii', True, battleship)
            screen.blit(message1, message1.get_rect(center = (600, 100)))
            screen.blit(message2, message2.get_rect(topleft = (100, 200)))
            screen.blit(message3, message3.get_rect(topleft = (100, 250)))
            screen.blit(message4, message4.get_rect(topleft = (100, 300)))
            screen.blit(message5, message5.get_rect(topleft = (100, 750)))
            screen.blit(message6, message6.get_rect(topleft = (100, 800)))
            screen.blit(message7, message7.get_rect(topleft = (100, 830)))
            start_button.draw()
        elif trial_count == 10:
            # only cover the area that's not the lightbulbs
            pygame.draw.rect(screen, porcelain, pygame.Rect(0, 0, window_width, 395))
            pygame.draw.rect(screen, porcelain, pygame.Rect(0, 0, 795, window_height))
            message1 = text_font.render('Game end!', True, jet)
            message2 = text_font_small.render('Your CP: '+str(chomsky_score), True, jet)
            message4 = text_font.render('Your sentences', True, jet)
            screen.blit(message1, message1.get_rect(center = (1050, 100)))
            screen.blit(message2, message2.get_rect(center = (1050, 200)))
            screen.blit(message4, message4.get_rect(topleft = (100, 50)))
            roll_all_sentences()
            quit_button.draw()
            restart_button.draw()
        else:
            for i in range(len(selected)):
                message = text_font.render(' '.join(selected[i]), True, jet)
                screen.blit(message, message.get_rect(topleft = (95, 150+(i*50))))
            score = text_font.render('CP: '+str(chomsky_score), True, jet)
            screen.blit(score, score.get_rect(topleft = (1050, 75)))
            for option in option_buttons:
                option.draw()
        pygame.display.flip()
        clock.tick(60)

    # quit game
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()