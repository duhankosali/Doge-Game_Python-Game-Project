"""
Platformer Game
"""
import arcade

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Doge Game"

# Constants used to scale our sprites from their original size
CHARACTER_SCALING = 1
TILE_SCALING = 0.5
COIN_SCALING = 0.5

SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = (SPRITE_PIXEL_SIZE * TILE_SCALING)

# Movement speed of player, in pixels per frame
#PLAYER_MOVEMENT_SPEED = 10
GRAVITY = 1
#PLAYER_JUMP_SPEED = 20

# How many pixels to keep as a minimum margin between the character
# and the edge of the screen.
LEFT_VIEWPORT_MARGIN = 200
RIGHT_VIEWPORT_MARGIN = 200
BOTTOM_VIEWPORT_MARGIN = 150
TOP_VIEWPORT_MARGIN = 100

# Karakterin Başlangıç yeri
PLAYER_START_X = 64
PLAYER_START_Y = 225


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):

        # Call the parent class and set up the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Oyun müziği oyun açıldığında aktif ediliyor.
        self.gamesound = True

        # Karakterin zıplama ve hareket hızı
        self.playerspeed = 10
        self.playerjumpspeed = 20

        # These are 'lists' that keep track of our sprites. Each sprite should
        # go into a list.
        self.coin_list = None
        self.wall_list = None
        self.player_list = None

        self.foreground_list = None
        self.background_list = None
        self.dont_touch_list = None
        self.buz_list = None
        self.ladder_list = None


        # Separate variable that holds the player sprite
        self.player_sprite = None

        # Our physics engine
        self.physics_engine = None

        # Used to keep track of our scrolling
        self.view_bottom = 0
        self.view_left = 0

        # Keep track of the score
        self.score = 0

        # Keep track of the your dead
        self.donttouch_counter = 0

        # Where is the right edge of the map?
        self.end_of_map = None
        self.exit_of_game = None

        # Level
        self.level = 1 # Harita bittiğinde level artıyor ve diğer haritaya geçiyoruz.

        # Müzik efektleri
        self.collect_coin_sound = arcade.load_sound(":resources:sounds/coin1.wav")
        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")
        self.game_over = arcade.load_sound(":resources:sounds/gameover1.wav") #Yeni ses efektimiz. Karakter ölünce çalışıyor.
        self.background_sound = arcade.load_sound("C:/Users/duhan/Desktop/ÜNİVERSİTE/BEYKOZ/Beykoz2 Dönem2/Mühendislik Projesi 2/platform_tutorial/tothemoon.mp3")

    def setup(self, level):
        """ Set up the game here. Call this function to restart the game. """

        # Used to keep track of our scrolling
        self.view_bottom = 0
        self.view_left = 0

        # Keep track of the score
        self.score = 0

        # Create the Sprite lists
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()

        self.foreground_list = arcade.SpriteList() #ön plan
        self.background_list = arcade.SpriteList() #arka plan
        self.end_of_map = arcade.SpriteList()
        self.exit_of_game = arcade.SpriteList()
        self.buz_list = arcade.SpriteList()


        # Set up the player, specifically placing it at these coordinates.
        image_source = "C:/Users/duhan/Desktop/ÜNİVERSİTE/BEYKOZ/Beykoz2 Dönem2/Mühendislik Projesi 2/platform_tutorial/yuruyendogem.png"
        self.player_sprite = arcade.Sprite(image_source, CHARACTER_SCALING)
        self.player_sprite.center_x = PLAYER_START_X
        self.player_sprite.center_y = PLAYER_START_Y
        self.player_list.append(self.player_sprite)

        # --- Load in a map from the tiled editor ---

        # Name of the layer in the file that has our platforms/walls
        platforms_layer_name = 'Platforms'
        moving_platforms_layer_name = 'Moving Platforms'

        # Name of the layer that has items for pick-up
        coins_layer_name = 'DogeCoin'

        # Name of the layer that has items for foreground
        foreground_layer_name = 'Foreground'

        # Name of the layer that has items for background
        background_layer_name = 'Background'

        # Name of the layer that has items we shouldn't touch
        dont_touch_layer_name = "Don't Touch"

        # Name of the layer that has finish map
        end_layer_name = 'End'
        exit_layer_name = "Exit"

        #Buzlu (Yürümek zor)
        buz_layer = 'Buz'

        # Map name
        map_name = f"C:/Users/duhan/Desktop/ÜNİVERSİTE/BEYKOZ/Beykoz2 Dönem2/Mühendislik Projesi 2/platform_tutorial/map2_level_{level}.tmx"

        # Read in the tiled map
        my_map = arcade.tilemap.read_tmx(map_name)

        # Calculate the right edge of the my_map in pixels
       # self.end_of_map = my_map.map_size.width * GRID_PIXEL_SIZE # !!!!!!!

        self.end_of_map = arcade.tilemap.process_layer(my_map,
                                                       end_layer_name,
                                                       TILE_SCALING,
                                                       use_spatial_hash=True)

        self.exit_of_game = arcade.tilemap.process_layer(my_map,
                                                       exit_layer_name,
                                                       TILE_SCALING,
                                                       use_spatial_hash=True)

        # -- Background
        self.background_list = arcade.tilemap.process_layer(my_map,
                                                            background_layer_name,
                                                            TILE_SCALING)
        # -- Background objects
        self.ladder_list = arcade.tilemap.process_layer(my_map,
                                                        "Ladders",
                                                        scaling=TILE_SCALING,
                                                        use_spatial_hash=True)

        # -- Foreground
        self.foreground_list = arcade.tilemap.process_layer(my_map,
                                                            foreground_layer_name,
                                                            TILE_SCALING)

        # -- Platforms
        self.wall_list = arcade.tilemap.process_layer(map_object=my_map,
                                                      layer_name=platforms_layer_name,
                                                      scaling=TILE_SCALING,
                                                      use_spatial_hash=True)

        # -- Moving Platforms #yeni
        moving_platforms_list = arcade.tilemap.process_layer(my_map, moving_platforms_layer_name, TILE_SCALING)
        for sprite in moving_platforms_list:
            self.wall_list.append(sprite)

        # -- Coins
        self.coin_list = arcade.tilemap.process_layer(my_map,
                                                      coins_layer_name,
                                                      TILE_SCALING,
                                                      use_spatial_hash=True)

        # -- Don't Touch Layer
        self.dont_touch_list = arcade.tilemap.process_layer(my_map,
                                                            dont_touch_layer_name,
                                                            TILE_SCALING,
                                                            use_spatial_hash=True)
        #yeni
        self.buz_list = arcade.tilemap.process_layer(map_object=my_map,
                                                      layer_name=buz_layer,
                                                      scaling=TILE_SCALING,
                                                      use_spatial_hash=True)

        # --- Other stuff
        # Levellere göre arka plan rengi değişiyor.

        if my_map.background_color:
            if(self.level==0):
                arcade.set_background_color(arcade.csscolor.BLACK)
            elif(self.level==1):
                arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)
            elif(self.level==2):
                arcade.set_background_color(arcade.csscolor.GRAY)
            elif(self.level==3):
                arcade.set_background_color(arcade.csscolor.SADDLE_BROWN)
            elif(self.level==4):
                arcade.set_background_color(arcade.csscolor.PURPLE)


        # Create the 'physics engine'
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite,
                                                             self.wall_list,
                                                             gravity_constant=GRAVITY,
                                                             ladders=self.ladder_list)

    def on_draw(self):
        """ Render the screen. """

        # Clear the screen to the background color
        arcade.start_render()

        # Draw our sprites --> Çizimler
        self.wall_list.draw()
        self.background_list.draw()
        self.coin_list.draw()
        self.dont_touch_list.draw()
        self.player_list.draw()
        self.foreground_list.draw()
        self.end_of_map.draw()
        self.exit_of_game.draw()
        self.ladder_list.draw()
        self.buz_list.draw()

        # Draw our score on the screen, scrolling it with the viewport
        score_text = f"Doge Coin: {self.score}"
        arcade.draw_text(score_text, 10 + self.view_left, 10 + self.view_bottom,
                         arcade.csscolor.BLACK, 18)

        dead_text = f"Kalan Hakkınız: {5-self.donttouch_counter}"
        arcade.draw_text(dead_text, 10 + self.view_left, 50 + self.view_bottom,
                         arcade.csscolor.BLACK, 18)

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if key == arcade.key.UP or key == arcade.key.W or key == arcade.key.SPACE:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = self.playerspeed
            elif self.physics_engine.can_jump():
                self.player_sprite.change_y = self.playerjumpspeed
                arcade.play_sound(self.jump_sound)
        elif key == arcade.key.DOWN or key == arcade.key.S:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = -self.playerspeed
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = -self.playerspeed
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = self.playerspeed


    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = 0
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = 0

    def update(self, delta_time):
        """ Movement and game logic """

        if (self.gamesound == True):
            arcade.play_sound(self.background_sound)
            self.gamesound = False

        # Move the player with the physics engine
        self.physics_engine.update()

        # Player ile Coinler arasında bir temas var mı?
        coin_hit_list = arcade.check_for_collision_with_list(self.player_sprite,
                                                             self.coin_list)
        buz_hit_list = arcade.check_for_collision_with_list(self.player_sprite,
                                                            self.buz_list)
        end_hit_list = arcade.check_for_collision_with_list(self.player_sprite,
                                                            self.end_of_map)
        exit_hit_list = arcade.check_for_collision_with_list(self.player_sprite,
                                                             self.exit_of_game)

        for end in end_hit_list:
            self.playerspeed = 10
            self.playerjumpspeed = 20

        for buz in buz_hit_list:
            self.playerspeed = 3
            self.playerjumpspeed = 5

        # Loop through each coin we hit (if any) and remove it
        for coin in coin_hit_list:
            # Remove the coin
            coin.remove_from_sprite_lists()
            # Play a sound
            arcade.play_sound(self.collect_coin_sound)
            # Add one to the score
            self.score += 1

        for exit in exit_hit_list:
            exit.remove_from_sprite_lists()
            self.level = 6
            self.setup(self.level)

        # Player ile Bayrak arasında bir temas var mı?
        door_hit_list = arcade.check_for_collision_with_list(self.player_sprite,
                                                             self.end_of_map)

        for door in door_hit_list:
            # Bayrak silinsin
            door.remove_from_sprite_lists()
            # Play a sound
            # Müzik Sonradan eklerim.
            # Level artsın.
            self.level += 1
            self.setup(self.level)

        # Track if we need to change the viewport
        changed_viewport = False

        # KARAKTERİN ÖLÜP YENİDEN DOĞMASI

        # Oyuncu haritadan düştü mü?
        if self.player_sprite.center_y < -1000:
            self.player_sprite.center_x = PLAYER_START_X
            self.player_sprite.center_y = PLAYER_START_Y
            self.donttouch_counter = self.donttouch_counter + 1  # Ölüm sayınızı tutar
            if (self.donttouch_counter == 5):
                self.level = 0
                self.donttouch_counter = 0
            # Set the camera to the start
            self.view_left = 0
            self.view_bottom = 0
            changed_viewport = True
            arcade.play_sound(self.game_over)


        # Oyuncu dokunmaması gereken bir şeye dokundu mu?
        if arcade.check_for_collision_with_list(self.player_sprite,
                                                self.dont_touch_list):
            self.player_sprite.change_x = 0
            self.player_sprite.change_y = 0
            self.player_sprite.center_x = PLAYER_START_X
            self.player_sprite.center_y = PLAYER_START_Y
            self.donttouch_counter = self.donttouch_counter + 1 # Ölüm sayınızı tutar
            if (self.donttouch_counter == 5):
                self.level = 0
                self.donttouch_counter = 0


            # Set the camera to the start
            self.view_left = 0
            self.view_bottom = 0
            changed_viewport = True
            arcade.play_sound(self.game_over)

            # Load the next level
            self.setup(self.level)

            # Set the camera to the start
            self.view_left = 0
            self.view_bottom = 0
            changed_viewport = True

        # --- Manage Scrolling ---

        # Scroll left
        left_boundary = self.view_left + LEFT_VIEWPORT_MARGIN
        if self.player_sprite.left < left_boundary:
            self.view_left -= left_boundary - self.player_sprite.left
            changed_viewport = True

        # Scroll right
        right_boundary = self.view_left + SCREEN_WIDTH - RIGHT_VIEWPORT_MARGIN
        if self.player_sprite.right > right_boundary:
            self.view_left += self.player_sprite.right - right_boundary
            changed_viewport = True

        # Scroll up
        top_boundary = self.view_bottom + SCREEN_HEIGHT - TOP_VIEWPORT_MARGIN
        if self.player_sprite.top > top_boundary:
            self.view_bottom += self.player_sprite.top - top_boundary
            changed_viewport = True

        # Scroll down
        bottom_boundary = self.view_bottom + BOTTOM_VIEWPORT_MARGIN
        if self.player_sprite.bottom < bottom_boundary:
            self.view_bottom -= bottom_boundary - self.player_sprite.bottom
            changed_viewport = True

        if changed_viewport:
            # Only scroll to integers. Otherwise we end up with pixels that
            # don't line up on the screen
            self.view_bottom = int(self.view_bottom)
            self.view_left = int(self.view_left)

            # Do the scrolling
            arcade.set_viewport(self.view_left,
                                SCREEN_WIDTH + self.view_left,
                                self.view_bottom,
                                SCREEN_HEIGHT + self.view_bottom)


def main():
    """ Main method """
    window = MyGame()
    window.setup(window.level)
    arcade.run()


if __name__ == "__main__":
    main()