import logging
import os
import platform
import random
import discord
import asyncio 
from openai import OpenAI

from jobspy import scrape_jobs
from discord.ext import commands, tasks
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String

WHITELIST_COMPANY_IDS = {
    "KPOPCENTER" : 101002223,
    "K-PLAY! FEST" : 79535575,
    "POP TOKKI" : 90526886,
    "WEVERSE AMERICA INC." : 90427386,
    "Goldenvoice" : 85104963,
    "HYBE America" : 81911983,
    "EVERLAST KOREA" : 80798089,
    "miHoYo" : 79090097,
    "Kpopconcerts" : 74027290,
    "Helix Publicity" : 72643108,
    "KpopWise" : 65849007,
    "Studio PAV" : 28968657,
    "hello82" : 26573466, 
    "WEBTOON" : 18913480,
    "Gen.G" : 18148981,
    "KOHAI" : 17963078,
    "DIVE Studios" : 14735324,
    "Nexon America" : 13282,
    "The Orchard" : 19615,
    "The Lippin Group" : 27326,
    "Crunchyroll" : 167212,
    "CJ ENM America" : 60880015,
    "Cloud9 Esports" : 3837963,
    "Spotify" : 207470,
}

intents = discord.Intents.default()
Base = declarative_base()

class FullTimeJob(Base):
    __tablename__ = "full_time_jobs"
    id = Column(Integer, primary_key=True)
    description = Column(String)
    job_id = Column(String, unique=True)
    application_url = Column(String)
    job_title = Column(String)
    company_name = Column(String)
    company_url = Column(String)
    location = Column(String)

class InternJob(Base):
    __tablename__ = "intern_jobs"
    id = Column(Integer, primary_key=True)
    description = Column(String)
    job_id = Column(String, unique=True)
    application_url = Column(String)
    job_title = Column(String)
    company_name = Column(String)
    company_url = Column(String)
    location = Column(String)

class NG2025Job(Base):
    __tablename__ = "ng_2025_jobs"
    id = Column(Integer, primary_key=True)
    description = Column(String)
    job_id = Column(String, unique=True)
    application_url = Column(String)
    job_title = Column(String)
    company_name = Column(String)
    company_url = Column(String)
    location = Column(String)

class NG2024Job(Base):
    __tablename__ = "ng_2024_jobs"

    id = Column(Integer, primary_key=True)
    description = Column(String)
    job_id = Column(String, unique=True)
    application_url = Column(String)
    job_title = Column(String)
    company_name = Column(String)
    company_url = Column(String)
    location = Column(String)

class LoggingFormatter(logging.Formatter):
    black = "\x1b[30m"
    red = "\x1b[31m"
    green = "\x1b[32m"
    yellow = "\x1b[33m"
    blue = "\x1b[34m"
    gray = "\x1b[38m"
    reset = "\x1b[0m"
    bold = "\x1b[1m"

    COLORS = {
        logging.DEBUG: gray + bold,
        logging.INFO: blue + bold,
        logging.WARNING: yellow + bold,
        logging.ERROR: red,
        logging.CRITICAL: red + bold,
    }

    def format(self, record):
        log_color = self.COLORS[record.levelno]
        format = "(black){asctime}(reset) (levelcolor){levelname:<8}(reset) (green){name}(reset) {message}"
        format = format.replace("(black)", self.black + self.bold)
        format = format.replace("(reset)", self.reset)
        format = format.replace("(levelcolor)", log_color)
        format = format.replace("(green)", self.green + self.bold)
        formatter = logging.Formatter(format, "%Y-%m-%d %H:%M:%S", style="{")
        return formatter.format(record)

logger = logging.getLogger("discord_bot")
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setFormatter(LoggingFormatter())
file_handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
file_handler_formatter = logging.Formatter(
    "[{asctime}] [{levelname:<8}] {name}: {message}", "%Y-%m-%d %H:%M:%S", style="{"
)
file_handler.setFormatter(file_handler_formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

engine = create_engine("sqlite:///jobs.db", echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

class DiscordBot(commands.Bot):
    def __init__(self, s=None) -> None:
        super().__init__(
            command_prefix=None,
            intents=intents,
            help_command=None,
        )
        self.logger = logger
        self.chatgpt_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.session = s

    @tasks.loop(minutes=1.0)
    async def status_task(self) -> None:
        await self.change_presence(activity=discord.Game('with jobs! 🎉'))

    @status_task.before_loop
    async def before_status_task(self) -> None:
        await self.wait_until_ready()

    async def setup_hook(self) -> None:
        self.logger.info(f"Logged in as {self.user.name}")
        self.logger.info(f"discord.py API version: {discord.__version__}")
        self.logger.info(f"Python version: {platform.python_version()}")
        self.logger.info(
            f"Running on: {platform.system()} {platform.release()} ({os.name})"
        )
        self.logger.info("-------------------")
        self.status_task.start()

    async def post_jobs(self, jobs, channel_id: int):
        target_channel = self.get_channel(channel_id)
        if target_channel is None:
            self.logger.error(f"No channel with ID {channel_id} found.")
            return 

        try:
            for index, row in jobs.iterrows():
                query = self.session.query(FullTimeJob).filter(FullTimeJob.job_id == row['id']).first()
                if query is None:
                    job_info = f""">>> ## {''.join(random.choices(['🎉', '👏', '💼', '🔥', '💻'], k=1))} [{row['company']}](<{row['company_url']}>) just posted a new job! 

### **Role:** 
[**{row['title']}**](<{row['job_url']}>)

### **Location:** 
{row['location']}
---
                """
                    await target_channel.send(job_info)
                    self.session.add(FullTimeJob(job_id=row['id'], application_url=row['job_url'], job_title=row['title'],
                                                company_name=row['company'], company_url=row['company_url']))
                    self.logger.info(f"Posting {row['title']}, {row['company']}, {row['job_url']}")

        except Exception as e:
            self.logger.error(f"Error processing new jobs: {e}")
            self.session.rollback()
        else:
            self.session.commit()

    @tasks.loop(seconds=0)
    async def job_posting_task(self):
        await self.job_task()
        await asyncio.sleep(10)
        self.logger.info("Job posting task completed.")

    async def job_task(self):
        channel_id = int(os.getenv('CHANNEL_ID'))
        full_time_jobs = scrape_jobs(linkedin_company_ids=list(WHITELIST_COMPANY_IDS.values()), site_name=['linkedin'])
        await self.post_jobs(full_time_jobs, channel_id)

    async def on_ready(self):
        print('ready')
        self.job_posting_task.start()

try:
    load_dotenv()
    bot = DiscordBot(s=session)
    bot.run(os.getenv("TOKEN"))
except:
    session.close()