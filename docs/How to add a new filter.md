Here's the instruction on how to add a new filter.

In the filters folder, add yourfilter.py. Copy one of the old filters for advice.

Then, go to carousel.py and add your filter in the dict:

catalog: dict[str, Callable[..., Any]] = {
        'painterly': painterly_filter,
        'watercolor': watercolor,
        'oil painting': oil_painting,
        'mosaic': mosaic_filter,
        'grayscale cartoon': gs_cartoon_filter,
        'anime style': animeFilter.filter,
        'pointillism': pointillism,
        'testfilter': testfilter
    }

I'm not sure, but I think the name on the left needs to not have underscores ( this thing: _ ). 

Then, add a background in filter_images_lib for your filter in background.py. Otherwise, the program will not work :D

def switchBackground(self, current_filter: str):
        filter_images_lib = {
            'painterly': 'painterly_bg.jpg',
            'watercolor': 'watercolor_bg.jpeg',
            'oil painting': 'oil_painting_bg.jpg',
            'mosaic': 'mosaic_bg.jpeg',
            'grayscale cartoon': 'gs_cartoon_bg_2.jpeg',
            'anime style': 'anime_bg.jpg',
            'pointillism': 'pointillism_bg.jpg',
            'testfilter': 'testimage.jpg'
        }