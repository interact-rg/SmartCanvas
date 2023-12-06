import itertools


class InstructionsLanguage:
    def __init__(self):
        self.instruction_language_sets = {
            "english": {
                "code": "en",
                "gdpr_consent": "Do you allow the saving of your pictures?",
                "filter_message": "Current filter is: ",
                "help_1": "Show 5 fingers to take a picture!",
                "help_2": "Show 2 fingers to change filter",
                "help_3": "Show 10 fingers to change language",
                "idle_text_1": "SmartCanvas",
                "idle_text_2": "Wave your hand and start your artistic experience",
                "image_showing_promote": "Wave hand to create another artwork",
                "filter_list": {
                    "painterly": "painterly",
                    "watercolor": "watercolor",
                    "oil painting": "oil painting",
                    "mosaic": "mosaic",
                    "grayscale cartoon": "grayscale cartoon",
                    "anime style": "anime style",
                    "pointillism": "pointillism"
                }
            },
            "finnish": {
                "code": "fi",
                "gdpr_consent": "Sallitko kuviesi tallentamisen?",
                "filter_message": "Nykyinen suodatin on: ",
                "help_1": "Näytä 5 sormea ottaaksesi kuvan!",
                "help_2": "Näytä 2 sormea vaihtaaksesi suodatinta",
                "help_3": "Näytä 10 sormea vaihtaaksesi kieltä",
                "idle_text_1": "SmartCanvas",
                "idle_text_2": "Heilauta kättäsi ja aloita taiteellinen kokemuksesi",
                "image_showing_promote": "Heilauta kättä luodaksesi toisen taideteoksen",
                "filter_list": {
                    "painterly": "maalauksellinen",
                    "watercolor": "akvarelli",
                    "oil painting": "öljyvärimaalaus",
                    "mosaic": "mosaiikki",
                    "grayscale cartoon": "grayscale cartoon",
                    "anime style": "anime style",
                    "pointillism": "pointillism"
                }
            }
        }

        self.instruction_set_iterator = itertools.cycle(self.instruction_language_sets)
        self.current_instruction_set = None
        self.next_instruction_set()

    def next_instruction_set(self):
        self.current_instruction_set = self.instruction_language_sets[next(self.instruction_set_iterator)]
