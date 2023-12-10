from PIL import Image, ImageSequence
import pygame
import sys
import random
import os
import time

# Variables pour la logique du jeu
current_arrow = None
last_arrow_time = None
arrow_delay = 3.0  # Délai initial en secondes

# Initialiser Pygame
pygame.init()

# Fonction pour charger un GIF et le convertir en une séquence d'images Pygame
def load_gif(file_path):
    pil_image = Image.open(file_path)
    frames = []
    for frame in ImageSequence.Iterator(pil_image):
        frame = frame.convert('RGBA')
        pygame_image = pygame.image.fromstring(
            frame.tobytes(), frame.size, frame.mode)
        frames.append(pygame_image)
    return frames

# Définir la taille de la fenêtre
size = (800, 600)
screen = pygame.display.set_mode(size)
screen_center = (size[0] // 2, size[1] // 2)

# Définir le titre de la fenêtre
pygame.display.set_caption("Jeu de Flèches")

# États du jeu
MENU, RULES, GAME, END_SCREEN = "menu", "rules", "game", "end_screen"

# Variable pour vérifier si les règles ont déjà été affichées
rules_shown = False

game_state = MENU

# Définir les polices
font = pygame.font.Font(None, 36)

# Créer des surfaces de texte
text_play = font.render('Jouer', True, (255, 255, 255))
text_quit = font.render('Quitter', True, (255, 255, 255))

# Définir les polices pour le chronomètre
timer_font = pygame.font.Font(None, 50)

# Initialiser le score
score = 0
# Définir une police pour le score
score_font = pygame.font.Font(None, 36)

# Positionner le texte
text_play_rect = text_play.get_rect(center=(400, 250))
text_quit_rect = text_quit.get_rect(center=(400, 350))

# Définir une police plus grande pour le titre du jeu
title_font = pygame.font.Font(None, 72)
title_text = title_font.render('Flèche Folie', True, (255, 215, 0))  # Or pour le titre
title_text_shadow = title_font.render('Flèche Folie', True, (0, 0, 0))  # Ombre noire pour le titre
title_rect = title_text.get_rect(center=(size[0] // 2, size[1] // 4))

# Déterminer si l'application est empaquetée (frozen) ou en cours d'exécution depuis le code source
if getattr(sys, 'frozen', False):
    application_path = sys._MEIPASS
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

# Utiliser application_path pour construire les chemins d'accès aux ressources
image_folder = os.path.join(application_path, 'image')
background_folder = os.path.join(image_folder, 'fond')
highscore_file_path = os.path.join(application_path, 'highscore.txt')

# Charger l'image de fond et les GIFs en utilisant les chemins ajustés
background_image = pygame.image.load(os.path.join(background_folder, 'fond.png'))

# Charger les GIFs en tant que séquences d'images
arrow_gifs = {
    'UP': load_gif(os.path.join(image_folder, 'haut.gif')),
    'DOWN': load_gif(os.path.join(image_folder, 'bas.gif')),
    'LEFT': load_gif(os.path.join(image_folder, 'gauche.gif')),
    'RIGHT': load_gif(os.path.join(image_folder, 'droite.gif'))
}

# Ajouter des textes pour l'écran de fin
text_restart = font.render('Recommencer', True, (255, 255, 255))
text_menu = font.render('Menu Principal', True, (255, 255, 255))
text_restart_rect = text_restart.get_rect(center=(400, 250))
text_menu_rect = text_menu.get_rect(center=(400, 350))

# Fonction pour charger le meilleur score
def load_highscore():
    try:
        with open(highscore_file_path, 'r') as file:
            return int(file.read())
    except FileNotFoundError:
        return 0

# Fonction pour enregistrer le meilleur score
def save_highscore(new_highscore):
    with open(highscore_file_path, 'w') as file:
        file.write(str(new_highscore))

# Charger le meilleur score au démarrage
highscore = load_highscore()

# Fonction pour afficher une flèche
def show_arrow():
    arrow = random.choice(list(arrow_gifs.keys()))
    return arrow

# Définir le texte pour les règles
rules_text_lines = [
    "Règles du jeu:",
    "1. Appuyez sur la flèche correspondante avant que",
    "le temps ne s'écoule.",
    "2. Le temps s'accélère après chaque flèche réussie.",
    "Appuyez sur 'Entrée' pour commencer à jouer."
]
rules_text = [font.render(line, True, (255, 255, 255)) for line in rules_text_lines]

# Boucle principale du jeu
running = True
current_arrow = None
frame_index = 0  # Index pour suivre le cadre actuel
frame_delay = 0.025  # Délai en secondes, ajustez selon vos besoins
last_frame_time = time.time()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_state == MENU:
            # Dessiner le meilleur score sur le menu principal
            highscore_text = score_font.render(f"Meilleur Score: {highscore}", True, (255, 255, 255))  # Blanc pour le meilleur score
            highscore_rect = highscore_text.get_rect(center=(size[0] // 2, size[1] // 2))
            screen.blit(highscore_text, highscore_rect)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:  # Choisir 'Jouer'
                    if not rules_shown:
                        game_state = RULES
                    else:
                        game_state = GAME
                        current_arrow = None
                        last_arrow_time = time.time()
                        arrow_delay = 3.0
                        score = 0
                elif event.key == pygame.K_DOWN:  # Choisir 'Quitter'
                    running = False

        elif game_state == RULES:
            # Afficher les règles
            for i, line in enumerate(rules_text):
                screen.blit(line, (50, 150 + i * 30))

            # Attendre que l'utilisateur appuie sur Entrée pour commencer
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    game_state = GAME
                    current_arrow = None
                    last_arrow_time = time.time()
                    arrow_delay = 3.0
                    score = 0
                    rules_shown = True  # Ne plus afficher les règles à l'avenir

        elif game_state == GAME:
            if current_arrow:
                # Obtenez le temps actuel
                current_time = time.time()

                # Vérifiez si suffisamment de temps s'est écoulé depuis le dernier changement de cadre
                if current_time - last_frame_time > frame_delay:
                    # Mettez à jour le cadre seulement si le délai est écoulé
                    frame_index = (frame_index + 1) % len(arrow_gifs[current_arrow])
                    last_frame_time = current_time

                frame = arrow_gifs[current_arrow][frame_index]
                frame_rect = frame.get_rect(center=screen_center)
                screen.blit(frame, frame_rect)

                # Calculer le temps restant et l'afficher
                time_left = max(0, arrow_delay - (current_time - last_arrow_time))
                timer_text = timer_font.render(f"{time_left:.2f}", True, (255, 0, 0))  # Rouge pour le chrono
                timer_rect = timer_text.get_rect(center=(size[0] // 2, 50))  # Positionnez le texte en haut au centre
                screen.blit(timer_text, timer_rect)

                # Si le temps est écoulé, passer à l'écran de fin
                if time_left == 0:
                    print("Temps écoulé !")
                    game_state = END_SCREEN
                    # Aucun besoin de continuer plus loin dans cette itération de la boucle
                    continue

            current_time = time.time()

            # Afficher une nouvelle flèche ou terminer le jeu si le temps est écoulé
            if not current_arrow or (current_time - last_arrow_time > arrow_delay):
                if current_arrow:
                    print("Trop lent!")
                    game_state = END_SCREEN
                    continue
                current_arrow = show_arrow()
                last_arrow_time = current_time

            # Gestion des touches en jeu
            if event.type == pygame.KEYDOWN:
                # Vérifier si la bonne touche est appuyée
                if ((event.key == pygame.K_UP and current_arrow == 'UP') or
                    (event.key == pygame.K_DOWN and current_arrow == 'DOWN') or
                    (event.key == pygame.K_LEFT and current_arrow == 'LEFT') or
                    (event.key == pygame.K_RIGHT and current_arrow == 'RIGHT')):
                    print("Correct!")
                    score += 1  # Augmenter le score
                    current_arrow = None
                    arrow_delay *= 0.95  # Augmenter la vitesse
                else:
                    print("Incorrect")
                    game_state = END_SCREEN  # Aller à l'écran de fin

            # Afficher le score
            score_text = score_font.render(f"Score: {score}", True, (255, 255, 255))  # Blanc pour le score
            score_rect = score_text.get_rect(center=(size[0] // 2, 100))  # Positionnez le score en haut au centre
            screen.blit(score_text, score_rect)

        elif game_state == END_SCREEN:
            # Vérifier si un nouveau score le plus élevé a été atteint
            if score > highscore:
                highscore = score
                save_highscore(highscore)

            # Afficher le score final
            final_score_text = score_font.render(f"Score Final: {score}", True, (255, 255, 255))  # Blanc pour le score final
            final_score_rect = final_score_text.get_rect(center=(size[0] // 2, 100))
            screen.blit(final_score_text, final_score_rect)

            # Gestion des événements de l'écran de fin
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:  # Choisir 'Recommencer'
                    game_state = GAME
                    current_arrow = None
                    last_arrow_time = time.time()
                    arrow_delay = 3.0
                    score = 0
                elif event.key == pygame.K_DOWN:  # Choisir 'Menu Principal'
                    game_state = MENU

    if game_state == END_SCREEN:
    # Vérifier si un nouveau score le plus élevé a été atteint
        if score > highscore:
            highscore = score
            save_highscore(highscore)

        # Afficher le score final
        final_score_text = score_font.render(f"Score Final: {score}", True, (255, 255, 255))  # Blanc pour le score final
        final_score_rect = final_score_text.get_rect(center=(size[0] // 2, 100))
        screen.blit(final_score_text, final_score_rect)

        # Gérer les événements dans l'écran de fin
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:  # Choisir 'Recommencer'
                    game_state = GAME
                    current_arrow = None
                    last_arrow_time = time.time()
                    arrow_delay = 3.0
                    score = 0
                elif event.key == pygame.K_DOWN:  # Choisir 'Menu Principal'
                    game_state = MENU

    # Effacer l'écran avec l'image de fond
    screen.blit(background_image, (0, 0))

    if game_state == MENU:
        # Dessiner le meilleur score sur le menu principal
        highscore_text = score_font.render(f"Meilleur Score: {highscore}", True, (255, 255, 255))  # Blanc pour le meilleur score
        highscore_rect = highscore_text.get_rect(center=(size[0] // 2, size[1] // 2))
        screen.blit(highscore_text, highscore_rect)

        # Dessiner l'ombre du titre puis le titre pour un effet de profondeur
        screen.blit(title_text_shadow, (title_rect.x + 2, title_rect.y + 2))  # Légèrement décalé pour l'effet d'ombre
        screen.blit(title_text, title_rect)

        # Dessiner le texte du menu
        screen.blit(text_play, text_play_rect)
        screen.blit(text_quit, text_quit_rect)

    elif game_state == RULES:
        # Afficher les règles
        for i, line in enumerate(rules_text):
            screen.blit(line, (50, 150 + i * 30))

    elif game_state == GAME:
        if current_arrow:
            # Obtenez le temps actuel
            current_time = time.time()

            # Vérifiez si suffisamment de temps s'est écoulé depuis le dernier changement de cadre
            if current_time - last_frame_time > frame_delay:
                # Mettez à jour le cadre seulement si le délai est écoulé
                frame_index = (frame_index + 1) % len(arrow_gifs[current_arrow])
                last_frame_time = current_time

            frame = arrow_gifs[current_arrow][frame_index]
            frame_rect = frame.get_rect(center=screen_center)
            screen.blit(frame, frame_rect)

            # Calculer le temps restant et l'afficher
            time_left = max(0, arrow_delay - (current_time - last_arrow_time))
            timer_text = timer_font.render(f"{time_left:.2f}", True, (255, 0, 0))  # Rouge pour le chrono
            timer_rect = timer_text.get_rect(center=(size[0] // 2, 50))  # Positionnez le texte en haut au centre
            screen.blit(timer_text, timer_rect)

            # Si le temps est écoulé, passer à l'écran de fin
            if time_left == 0:
                print("Temps écoulé !")
                game_state = END_SCREEN
                # Aucun besoin de continuer plus loin dans cette itération de la boucle
                continue

            # Afficher le score
            score_text = score_font.render(f"Score: {score}", True, (255, 255, 255))  # Blanc pour le score
            score_rect = score_text.get_rect(center=(size[0] // 2, 100))  # Positionnez le score en haut au centre
            screen.blit(score_text, score_rect)

    elif game_state == END_SCREEN:
    # Vérifier si un nouveau score le plus élevé a été atteint
        if score > highscore:
            highscore = score
            save_highscore(highscore)

        # Afficher le score final
        final_score_text = score_font.render(f"Score Final: {score}", True, (255, 255, 255))  # Blanc pour le score final
        final_score_rect = final_score_text.get_rect(center=(size[0] // 2, 100))

        screen.blit(final_score_text, final_score_rect)
        # Dessiner l'écran de fin
        screen.blit(text_restart, text_restart_rect)
        screen.blit(text_menu, text_menu_rect)

    # Mettre à jour l'écran
    pygame.display.flip()

# Quitter Pygame
pygame.quit()
sys.exit()