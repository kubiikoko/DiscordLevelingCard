from io import BufferedIOBase, BytesIO, IOBase
from os import PathLike
from typing import Optional, Union

from aiohttp import ClientSession
from PIL import Image, ImageDraw, ImageFont
from .error import InvalidImageType, InvalidImageUrl
from disnake import File as disnakeFile
from nextcord import File as nextcordFile

class RankCard:
    """Class for creating a rank cards

    Parameters
    ----------
    background: :class:`Union[PathLike, BufferedIOBase]`
        The background image for the rank card. This can be a path to a file or a file-like object in `rb` mode

    avatar: :class:`Union[PathLike, BufferedIOBase]`
        The avatar image for the rank card. This can be a path to a file or a file-like object in `rb` mode
    
    level: :class:`int`
        The level of the member
    
    username: :class:`str`
        The username of the member
    
    current_exp: :class:`int`
        The current amount of XP the member has
    
    max_exp: :class:`int`
        The amount of XP required for the member to level up
    
    bar_color: :class:`Optional[str]`
        The color of the XP bar. This can be a hex code or a color name. Default is `white`
    
    text_color: :class:`Optional[str]`
        The color of the text. This can be a hex code or a color name. Default is `white`
    
    path: :class:`Optional[PathLike]`
        The path to save the rank card to. If this is not provided, `bytes` that can be added to any discord.py fork's `File` class instead.
    
    type: :class:`Optional[str]`
        The type of the rank card. This can be `disnake`(returns `disnake.File` class) or `nextcord`(returns `nextcord.File class`). Default is `None`


    Attributes
    ----------
    - `background`
    - `avatar`
    - `level`
    - `username`
    - `current_exp`
    - `max_exp`
    - `bar_color`
    - `text_color`
    - `path`
    - `type`
    """

    __slots__ = ('background', 'avatar', 'level', 'username', 'current_exp', 'max_exp', 'bar_color', 'text_color', 'path', 'type')



    def __init__(
        self,
        background: Union[PathLike, BufferedIOBase],
        avatar: Union[PathLike, BufferedIOBase],
        level:int,
        username:str,
        current_exp:int,
        max_exp:int,
        bar_color:Optional[str]="white",
        text_color:Optional[str]="white",
        path:Optional[str]=None,
        type:Optional[str]=None
    )-> None:
        self.background = background
        self.avatar = avatar
        self.level = level
        self.username = username
        self.current_exp = current_exp
        self.max_exp = max_exp
        self.bar_color = bar_color
        self.text_color = text_color
        self.path = path
        self.type = type

    @staticmethod
    def convert_number(number: int) -> str:
        if number >= 1000000000:
            return f"{number / 1000000000:.1f}B"
        elif number >= 1000000:
            return f"{number / 1000000:.1f}M"
        elif number >= 1000:
            return f"{number / 1000:.1f}K"
        else:
            return str(number)

    @staticmethod
    async def image_(url:str):
        async with ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise InvalidImageUrl(f"Invalid image url: {url}")
                data = await response.read()
                return Image.open(BytesIO(data))



    async def card1(self)-> Union[None, bytes]:
        """
        Creates the rank card and saves it to the path provided in `self.path` or returns `bytes` if `self.path` is not provided
        
        ![card](https://cdn.discordapp.com/attachments/907213435358547968/1019966057294860328/final.png)
        """
        
        if isinstance(self.background, IOBase):
            if not (self.background.seekable() and self.background.readable() and self.background.mode == "rb"):
                raise InvalidImageType(f"File buffer {self.background!r} must be seekable and readable and in binary mode")
            self.background = Image.open(self.background)
        elif isinstance(self.background, str):
            if self.background.startswith("http"):
                self.background = await RankCard.image_(self.background)
            else:
                self.background = Image.open(open(self.background, "rb"))
        else:
            raise InvalidImageType(f"background must be a path or url or a file buffer, not {type(self.background)}") 

        if isinstance(self.avatar, IOBase):
            if not (self.avatar.seekable() and self.avatar.readable() and self.avatar.mode == "rb"):
                raise ValueError(f"File buffer {self.avatar!r} must be seekable and readable and in binary mode")
            self.avatar = Image.open(self.avatar)
        elif isinstance(self.avatar, str):
            if self.avatar.startswith("http"):
                self.avatar = await RankCard.image_(self.avatar)
            else:
                self.avatar = Image.open(open(self.avatar, "rb"))
        else:
            raise TypeError(f"avatar must be a path or url or a file buffer, not {type(self.background)}") 

        self.avatar = self.avatar.resize((170,170))

        overlay = Image.open("./assets/overlay1.png")
        background = Image.new("RGBA", overlay.size)
        backgroundover = self.background.resize((638,159))
        background.paste(backgroundover,(0,0))
        
        self.background = background.resize(overlay.size)
        self.background.paste(overlay,(0,0),overlay)

        myFont = ImageFont.truetype("./assets/levelfont.otf",40)
        draw = ImageDraw.Draw(self.background)

        draw.text((205,(327/2)+20), self.username,font=myFont, fill=self.text_color,stroke_width=1,stroke_fill=(0, 0, 0))
        bar_exp = (self.current_exp/self.max_exp)*420
        if bar_exp <= 50:
            bar_exp = 50    

        current_exp = RankCard.convert_number(self.current_exp)
        
        max_exp = RankCard.convert_number(self.max_exp)
        

        myFont = ImageFont.truetype("./assets/levelfont.otf",30)
        draw.text((197,(327/2)+125), f"LEVEL - {RankCard.convert_number(self.level)}",font=myFont, fill=self.text_color,stroke_width=1,stroke_fill=(0, 0, 0))

        w,h = draw.textsize(f"{current_exp}/{max_exp}", font=myFont)
        draw.text((638-w-50,(327/2)+125), f"{current_exp}/{max_exp}",font=myFont, fill=self.text_color,stroke_width=1,stroke_fill=(0, 0, 0))

        mask_im = Image.open("./assets/mask_circle.jpg").convert('L').resize((170,170))
        new = Image.new("RGB", self.avatar.size, (0, 0, 0))
        try:
            new.paste(self.avatar, mask=self.avatar.convert("RGBA").split()[3])
        except Exception as e:
            print(e)
            new.paste(self.avatar, (0,0))
        self.background.paste(new, (13, 65), mask_im)

        im = Image.new("RGB", (490, 51), (0, 0, 0))
        draw = ImageDraw.Draw(im, "RGBA")
        draw.rounded_rectangle((0, 0, 420, 50), 30, fill=(255,255,255,50))
        draw.rounded_rectangle((0, 0, bar_exp, 50), 30, fill=self.bar_color)
        self.background.paste(im, (190, 235))
        new = Image.new("RGBA", self.background.size)
        new.paste(self.background,(0, 0), Image.open("./assets/curvedoverlay.png").convert("L"))
        self.background = new.resize((505, 259))

        if self.path is not None:
            self.background.save(self.path, "PNG")
            return self.path
        elif self.type == "disnake":
            with BytesIO() as image:
                    self.background.save(image, 'PNG')
                    image.seek(0)
                    return disnakeFile(fp=image, filename="rank.png")
        elif self.type == "nextcord":
            with BytesIO() as image:
                    self.background.save(image, 'PNG')
                    image.seek(0)
                    return nextcordFile(fp=image, filename="rank.png")
        else:
            with BytesIO() as image:
                self.background.save(image, 'PNG')
                image.seek(0)
                return image