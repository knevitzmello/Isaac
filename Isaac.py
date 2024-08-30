import speech_recognition as sr

from utils import setup
from utils.voice import Voice

import pyttsx3

speaker=pyttsx3.init()

CONFIG_PATH = "config.json"
ADDONS_DIR = "addons"


class Isaac:

    """
    main Isaac instance
    """
    speaker.setProperty('voice', 'brazil')
    rate = speaker.getProperty('rate')
    speaker.setProperty('rate', rate+10)

    def __init__(self, config_file_path: str = CONFIG_PATH):
        """
        config_file_path: file path for config file
        """

        self.config_file_path = config_file_path

        self.setup()

        self.config = setup.load_config(self.config_file_path)
        self.settings = self.config["settings"]

        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.names = self.settings["names"]

        # voice intance
        self.voice_instance = Voice(self.config_file_path)

    def setup(self):
        """
        setting up Isaac
        """

        # create config file
        setup.create_config()

        # check config global file
        setup.check_global_config(self.config_file_path)

        # load addons
        setup.load_addons(self.config_file_path, ADDONS_DIR)

    def parse_args(self, command: str, keyword: str) -> list:
        """
        parse command arguments

        command: the command to parse
        keyword: the keyword that activated the command

        example: play song_name
        using keyword: play
        returns: [song_name]

        another example: play song_name by artist
        using keyword: play
        returns: [song_name, by, artist]
        """

        command_without_keywords = command.replace(keyword, "").strip()
        return command_without_keywords.split()

    def execute_command(self, command: str):
        """
        execute user command

        command: the command to execute
        """
        # aqui recebe o comando
        
        print(f"Executing {command}")
        command_executed = False
        addons = self.config["addons"]

        # match command to addon
        for addon in addons:
            for command_to_listen_for in addon["commands"]: # para cada comando configurado nos addons
                if command_to_listen_for in command: # Aqui é feito um reconhecimento do comando

                    addon = __import__(
                        f"{ADDONS_DIR}.{addon['developer']}_{addon['name']}.{addon['entry-point']}",
                        fromlist=["addons"],
                    )

                    # any possible errors should be handeled by developers
                    # within their addons, if an error is encountered, they
                    # will be ignored as to not halt/break the main instance


                    
                    try:
                        addon.run(
                            command_to_listen_for,
                            self.parse_args(command, command_to_listen_for),
                            self.voice_instance,
                        )
                    except:
                        pass

                    command_executed = True

        if not command_executed:
            speaker.say("Desculpe, não entendi")
            speaker.runAndWait()

    def parse_command(self, voice_input: str) -> str:
        """
        get command from user voice input

        voice_input: the user input as text
        """

        command = ""

        # check for name keyword
        for name in self.names:
            if name in voice_input:
                command = voice_input.split(name)[1].strip()
            else:
                print(f"{name} has not been called")

        return command

    def run(self):
        """
        run instance
        """

        try:
            while True:
                # adjusting for ambient noise
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source)
                    print("Ouvindo...")
                    audio = self.recognizer.listen(source)

                print("Comando capturado, iniciando reconhecimento...")
                try:
                    # recognize speech using Google Speech Recognition
                    voice_input = str(
                        self.recognizer.recognize_google(
                            audio, language=self.settings["lang"]
                        )
                    ).lower()

                    voice_input = "isaac que horas são" # inserção manual para debug
                    
                    # we need some special handling here to correctly print unicode characters to standard output
                    print(f"Voce disse: {voice_input}")

                    command = self.parse_command(voice_input)

                    if command:
                        self.execute_command(command)

                except sr.UnknownValueError:
                    print("Nao entendi.")
                except sr.RequestError as e:
                    print(
                        "Uh oh! Couldn't request results from Google Speech Recognition service; {0}".format(
                            e
                        )
                    )
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    Isaac = Isaac()
    Isaac.run()