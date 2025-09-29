# game_loop.py
import pygame

def run_replay(screen, adapter, renderer, event_interval=1.0):
    running = True
    clock = pygame.time.Clock()
    event_index = 0
    time_accumulator = 0  # tracks elapsed time

    while running:
        dt = clock.tick(60) / 1000  # convert milliseconds to seconds
        time_accumulator += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            call = renderer.check_clicked_buttons(event)
        # Advance simulation if enough time has passed
        if renderer.auto:
            if time_accumulator >= event_interval and event_index < len(adapter.history):
                adapter.state = adapter.history[event_index]
                event_index += 1
                time_accumulator = 0 # subtract interval so next event waits

        # Draw
        renderer.update_hover(pygame.mouse.get_pos())
        if adapter.state:
            renderer.draw_board(screen, adapter.state)

        pygame.display.flip()
