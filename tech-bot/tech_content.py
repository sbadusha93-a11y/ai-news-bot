import random
from datetime import datetime
import re

from tech_scripts import SCRIPT_TEMPLATES

ADULT_KEYWORDS = {
    "sex", "sexy", "sexual", "porn", "porno", "pornography", "nude", "naked",
    "erotic", "adult", "xxx", "18+", "nsfw", "lingerie", "bikini", "swimsuit",
    "model", "onlyfans", "camgirl", "escort", "dating", "hookup",
    "milf", "boobs", "hentai", "lewd", "horny", "slut", "whore",
    "bdsm", "fetish", "masturbat", "penis", "vagina",
    "breast", "nipple", "panties", "underwear", "nudity", "explicit",
    "mature", "sensual", "seductive", "provocative",
}

MEGA_ADULT_BLOCK = {
    "sex", "porn", "nude", "naked", "erotic", "xxx", "nsfw", "hentai",
    "onlyfans", "escort", "milf", "boobs", "lewd", "horny", "slut",
    "bdsm", "fetish", "masturbat", "penis", "vagina", "nipple",
}

TECH_LISTS = [
    {
        "title": "Top 10 AI Tools That Will Change Your Life in 2026",
        "hook_text": "AI Tools That Will Change Your Life",
        "intro": "Artificial intelligence is no longer science fiction. It is here, and it is transforming how we work, create, and live. These ten AI tools are not just impressive demos, they are practical tools you can use today to save hours, make better decisions, and unlock skills you never knew you had.",
        "items": [
            ("10", "ChatGPT", "OpenAI's ChatGPT remains the most versatile AI assistant ever created. The latest model can write code, analyze massive documents, generate images, and hold natural conversations. It is free to start and indispensable for anyone who works with information."),
            ("9", "Midjourney", "Midjourney is the gold standard for AI image generation. Its photorealistic output and artistic control let anyone become a designer. Marketers, creators, and small businesses use it to create professional visuals in seconds instead of hiring expensive designers."),
            ("8", "Notion AI", "Notion AI turns your notes into a thinking partner. It summarizes meetings, rewrites drafts, generates action items, and helps you brainstorm. It is the smartest productivity tool you can add to your workflow today."),
            ("7", "GitHub Copilot", "GitHub Copilot is an AI pair programmer that writes code alongside you. It suggests entire functions, catches bugs early, and explains complex code in plain English. A GitHub study found that developers using it completed tasks significantly faster."),
            ("6", "ElevenLabs", "ElevenLabs creates the most realistic AI voices in existence. You can clone any voice with just a minute of audio and generate speech that sounds completely natural. Podcasters, audiobook creators, and marketers are using it to scale content production."),
            ("5", "Perplexity AI", "Perplexity AI is the smartest search engine you have never used. Instead of a list of links, it gives you direct answers with real citations. It is perfect for research, fact-checking, and learning anything faster than traditional search ever allowed."),
            ("4", "RunwayML", "RunwayML lets you edit and generate video with AI. Remove backgrounds, generate new scenes, or create entire videos from text. Tasks that once took professional editors days now take minutes with zero experience required."),
            ("3", "Claude", "Claude by Anthropic is the best AI for deep analysis and long-form reasoning. It can process entire books in one go, analyze complex legal documents, and provide nuanced insights. Its safety-focused design makes it the most trusted AI for enterprise use."),
            ("2", "Otter.ai", "Otter.ai automatically joins your meetings, takes notes, and highlights action items. It works with Zoom, Google Meet, and Teams. You will never forget a decision or lose a brilliant idea that came up during a meeting again."),
            ("1", "Sora by OpenAI", "Sora is OpenAI's groundbreaking video generation model. Type any description and it creates a realistic video that matches your vision. Early users are already creating short films, marketing content, and animations that would have cost thousands to produce traditionally."),
        ],
        "outro": "Those are the top 10 AI tools that will change your life in 2026. How many of these have you tried? Let me know in the comments which one surprised you the most. If you found this helpful, hit that like button and subscribe for more tech insights. Thanks for watching.",
    },
    {
        "title": "Top 10 Productivity Apps You Need in 2026",
        "hook_text": "Productivity Apps You Need in 2026",
        "intro": "We all want to get more done in less time. These ten apps are carefully selected to help you organize your life, eliminate distractions, and focus on what actually matters. Here are the top 10 productivity apps you need in 2026.",
        "items": [
            ("10", "Todoist", "Todoist is the simplest and most powerful to-do list app available. Its natural language input lets you type tasks as you think them, and its smart scheduling suggests the best time to complete each one. It works on every device and syncs instantly."),
            ("9", "Arc Browser", "Arc is reinventing the web browser for modern work. It replaces chaotic tabs with organized spaces, lets you split screens easily, and includes built-in tools for notes and screenshots. Once you switch to Arc, you cannot go back to Chrome."),
            ("8", "Obsidian", "Obsidian is a thinking tool disguised as a note-taking app. It connects your notes like a personal wiki, creating a web of knowledge that grows smarter over time. It is free and completely offline, making it the most powerful second brain available."),
            ("7", "Motion", "Motion is an AI calendar that schedules your day automatically. It prioritizes your tasks, blocks focus time, and reschedules everything when meetings change. Users report getting twice as much done without feeling overwhelmed."),
            ("6", "Superhuman", "Superhuman is the fastest email client ever built. It is designed for speed, with keyboard shortcuts for everything, AI-powered triage, and built-in scheduling. The average user saves over four hours per week compared to Gmail."),
            ("5", "Linear", "Linear is the project management tool designed for modern teams. It is blazing fast, beautifully designed, and helps software teams move faster. Its real-time collaboration and smart prioritization make it the preferred choice for top tech companies."),
            ("4", "Readwise Reader", "Readwise Reader is the best app for saving and consuming content. It lets you save articles, newsletters, and PDFs, then highlights the best parts using AI. It turns your reading list into a personal briefing that you can actually finish."),
            ("3", "Cron", "Cron is a calendar app that looks and feels like it is from the future. It integrates with all your tools, shows exactly what matters, and makes scheduling meetings painless. It was acquired by Notion and is now free for everyone."),
            ("2", "Raycast", "Raycast replaces your Mac's Spotlight with superpowers. It launches apps, runs calculations, controls your music, and connects to hundreds of extensions. You can do everything from your keyboard without ever touching your mouse."),
            ("1", "Whisper by OpenAI", "Whisper is the most accurate speech-to-text tool ever created. It transcribes audio with near-human accuracy, works in dozens of languages, and is completely free. Dictating your thoughts is faster than typing, and Whisper makes it flawless."),
        ],
        "outro": "Those are the top 10 productivity apps you need in 2026. How many are you already using? Drop your favorite productivity tool in the comments. If you learned about something new, like and subscribe for more tech recommendations. See you in the next video.",
    },
    {
        "title": "10 Mind-Blowing Tech Facts You Never Knew",
        "hook_text": "Mind-Blowing Tech Facts",
        "intro": "The technology we use every day is full of incredible stories and surprising secrets. These ten facts will change how you see the devices and services you rely on. Here are ten mind-blowing tech facts you probably never knew.",
        "items": [
            ("10", "The First Computer Bug", "In 1947, Grace Hopper found a moth trapped in a relay of the Harvard Mark II computer. She taped it into the logbook and wrote first actual case of bug being found. While the term bug was used in engineering before, this incident popularized debugging in computing."),
            ("9", "Google's LEGO Storage", "Larry Page and Sergey Brin built the storage case for their first ten hard drives using LEGO bricks. It was cheap, expandable, and held the entire early Google search index. The servers themselves were standard PCs, but the LEGO casing became an iconic story."),
            ("8", "The QWERTY Layout", "The QWERTY keyboard layout was created in 1873 for the Sholes and Glidden typewriter. It placed common letter pairs apart to reduce mechanical jams on early typewriters. The layout became the standard and we still use it today."),
            ("7", "Netflix Was a DVD Rental", "Netflix originally mailed DVDs in paper envelopes. The company sent over five billion discs before pivoting to streaming. The last DVD was mailed in 2023, ending a twenty-five year era. Reed Hastings started the company after a forty dollar late fee."),
            ("6", "The First Website Is Still Online", "The very first website ever created is still online. Tim Berners-Lee created info.cern.ch in 1990 to explain the World Wide Web project. You can visit it today and see how far the internet has come."),
            ("5", "A Floppy Disk Launched Windows 95", "Windows 95 was shipped on thirteen floppy disks. The entire operating system was compressed to fit on disks that held less than two megabytes each. Today, that same data would fit in a single email attachment."),
            ("4", "More Phones Than People", "There are more mobile phones than people on Earth. Over eight billion active mobile devices exist today, outnumbering the human population. Many people in developing countries access the internet exclusively through their phones."),
            ("3", "The First Gigantic Hard Drive", "The first hard drive, introduced in 1956 by IBM, weighed over a ton. The IBM 350 stored just five megabytes of data and was transported by forklift. Today, a microSD card smaller than your fingernail can hold over one million times more data."),
            ("2", "CAPTCHA Helps Digitize Books", "Every time you solve a CAPTCHA, you are helping digitize books. reCAPTCHA shows words from old books and newspapers that optical character recognition cannot read. Your answers help preserve human knowledge one word at a time."),
            ("1", "The Internet of Interesting Estimates", "One physicist estimated that the weight of all electrons moving through the internet at any given moment is about fifty grams. It is a fun thought experiment rather than a precise measurement, but it gives a new perspective on the scale of the digital world."),
        ],
        "outro": "Those are ten mind-blowing tech facts you probably never knew. Which fact shocked you the most? Let me know in the comments. If you learned something new, smash that like button and subscribe for more fascinating tech content. Thanks for watching.",
    },
    {
        "title": "Top 10 Free Tech Tools That Are Better Than Paid Alternatives",
        "hook_text": "Free Tech Tools Better Than Paid",
        "intro": "You do not need to spend money to get the best tools. Some of the most powerful software in the world is completely free. These ten free tools are not just good for free, they are genuinely better than paid alternatives used by millions.",
        "items": [
            ("10", "VS Code", "Microsoft's VS Code is the most popular code editor in the world and it is completely free. It has thousands of extensions, built-in Git support, and an integrated terminal. Paid editors like Sublime Text and WebStorm cannot match its ecosystem."),
            ("9", "DaVinci Resolve", "DaVinci Resolve is a professional video editor used by Hollywood studios. It includes color grading, visual effects, and audio post-production. The free version has more features than Adobe Premiere Pro which costs hundreds per year."),
            ("8", "Bitwarden", "Bitwarden is an open-source password manager that is free for unlimited devices. Paid alternatives like LastPass and 1Password charge over thirty dollars per year. Bitwarden is more secure because its code is publicly audited by security experts."),
            ("7", "OBS Studio", "OBS Studio is the industry standard for live streaming and screen recording. It powers most streams on Twitch and YouTube. Paid alternatives like XSplit cost money while OBS is free and has more features."),
            ("6", "Krita", "Krita is a professional painting program built by artists for artists. It has brush engines, animation tools, and color management that compete with Adobe Photoshop. The paid version does not exist because everything is free."),
            ("5", "GIMP", "GIMP is the original free Photoshop alternative. It has been developed for over twenty-five years and includes advanced photo retouching, image composition, and graphic design tools. It lacks nothing that the average user needs from Photoshop."),
            ("4", "Audacity", "Audacity is the most popular audio editing software in the world. It records, edits, and mixes audio with professional quality. Podcasters, musicians, and voice actors rely on it daily. Paid editors like Adobe Audition offer little extra for most users."),
            ("3", "Brave Browser", "Brave is a privacy-focused browser that blocks ads and trackers by default. It is faster than Chrome because it removes the junk that slows pages down. Built-in Tor integration makes it more private than any paid VPN service."),
            ("2", "Blender", "Blender is a fully-featured 3D creation suite used by professional studios. It handles modeling, animation, rendering, and video editing. Major films and games use Blender. Paid software like Maya costs over two thousand dollars per year."),
            ("1", "The Best Tool Is the One You Already Have", "The most powerful free tool is the device in your pocket. Smartphones today have more computing power than NASA had when it landed a man on the moon. The best tool is the one you already own and the willingness to learn how to use it fully."),
        ],
        "outro": "Those are ten free tech tools that are genuinely better than paid alternatives. How many of these are you already using? Let me know in the comments if we missed any. If you found this valuable, like and subscribe for more tech content. See you next time.",
    },
    {
        "title": "Top 10 Websites You Did Not Know Existed But Absolutely Should",
        "hook_text": "Websites You Did Not Know Existed",
        "intro": "The internet is vast and full of hidden gems. These ten websites are not the ones everyone talks about, but they are incredibly useful, fascinating, and will make you wonder how you ever lived without them. Here are ten websites you probably never knew existed.",
        "items": [
            ("10", "Photopea", "Photopea is a fully-featured Photoshop clone that runs entirely in your browser. You can open PSD files, edit layers, and export high-quality images. It works on any device with a browser and requires no signup or payment."),
            ("9", "FutureMe", "FutureMe lets you send an email to your future self. Write a message today and choose when you want to receive it, from one year to ten years from now. It is a powerful tool for reflection and tracking how much you have grown."),
            ("8", "Humaans", "Humaans is a beautifully designed HR platform that is free for small teams. It manages employees, time off, and documents. The design is so good that it makes you actually want to do HR tasks."),
            ("7", "Excalidraw", "Excalidraw is a virtual whiteboard that creates hand-drawn style diagrams. It is perfect for brainstorming, flowcharts, and wireframes. The drawings look charmingly rough while being incredibly precise."),
            ("6", "Radio Garden", "Radio Garden lets you explore live radio stations from around the world on a globe interface. Spin the Earth and tap any green dot to hear local radio from that city. It is the most beautiful way to discover music and culture from everywhere."),
            ("5", "Remove.bg", "Remove.bg removes the background from any image in seconds with AI. It is shockingly accurate and handles hair, fur, and complex edges better than professional Photoshop users. The basic version is free and requires no account."),
            ("4", "JustWatch", "JustWatch tells you where to stream any movie or TV show legally. Search a title and it shows which services have it, whether it is free with subscription, and how much it costs to rent. No more searching through five apps to find something to watch."),
            ("3", "This Is Sand", "This Is Sand is a relaxing, mesmerizing website where you pour colored sand into a virtual jar. It has no goal, no points, and no ads. It is strangely therapeutic and a perfect way to unwind for a few minutes."),
            ("2", "Sunsama", "Sunsama is a daily planner that combines your calendar and tasks into one view. It helps you plan realistic daily schedules and actually finish what you start. A calm approach to productivity that beats noisy project management tools."),
            ("1", "The Internet Archive", "The Internet Archive is a non-profit digital library that preserves the entire internet. It has billions of web pages, millions of books, movies, and software. You can browse websites from 1996 and read books that are no longer in print. It is humanity's digital memory."),
        ],
        "outro": "Those are ten incredible websites you probably never knew existed. Which one are you going to try first? Let me know in the comments. If you discovered something useful, hit like and subscribe for more hidden internet gems. Thanks for watching.",
    },
    {
        "title": "10 Technology Predictions for the Next Decade",
        "hook_text": "Technology Predictions 2026-2036",
        "intro": "The pace of technological change is accelerating faster than ever. Looking ahead to the next ten years, experts predict transformations that will reshape every part of our lives. Here are ten bold predictions for where technology is heading.",
        "items": [
            ("10", "AI Will Write Most Code", "By 2030, artificial intelligence will write the majority of code in production. Human developers will shift from writing code to reviewing and guiding AI-generated software. Junior programming roles as we know them will largely disappear."),
            ("9", "Electric Vehicles Will Become the Default", "Electric vehicles will outsell combustion engines globally by 2028. Battery technology will improve to deliver over five hundred miles of range and charging times under fifteen minutes. Gas stations will begin to disappear from cities."),
            ("8", "AR Glasses Will Replace Smartphones", "Augmented reality glasses will begin replacing smartphones by the early 2030s. Companies like Apple, Meta, and Google are investing billions. You will wear your computer instead of carrying it, with everything appearing in your field of view."),
            ("7", "Quantum Computing Will Unlock New Science", "Practical quantum computers will solve problems that are impossible for classical computers. Drug discovery, climate modeling, and materials science will advance faster in five years than they have in the past fifty."),
            ("6", "Robots Will Enter Every Home", "Affordable general-purpose robots will become common in households by 2035. They will clean, cook, and assist with daily tasks. The cost will drop to that of a premium smartphone as production scales."),
            ("5", "Brain-Computer Interfaces Will Go Mainstream", "Neural interfaces that let you control devices with your mind will move from medical use to consumer products. Typing and clicking will feel as outdated as using a rotary phone. The first generation of thought-controlled computers will arrive by 2029."),
            ("4", "Space Travel Will Become Accessible", "Space tourism will become a real industry with prices dropping below fifty thousand dollars per person. Orbital hotels and lunar expeditions will be bookable. What was once reserved for governments will become a luxury travel option."),
            ("3", "AI-Generated Entertainment Will Dominate", "Most movies, music, and games will be created with significant AI assistance by 2032. Personalized entertainment generated in real-time for each viewer will become the norm. The concept of a single fixed version of a film will feel outdated."),
            ("2", "Your Health Will Be Tracked Continuously", "Wearable sensors and AI analysis will monitor your health twenty-four seven. Diseases will be detected years before symptoms appear. The shift from reactive to preventive medicine will add years to the average human lifespan."),
            ("1", "The Concept of Work Will Fundamentally Change", "The combination of AI, automation, and remote collaboration will redefine what work means. The forty-hour work week and the five-day office schedule will become historical artifacts. People will focus on creativity and strategy while AI handles routine tasks. Entire career paths that exist today will disappear and new ones we cannot imagine will emerge."),
        ],
        "outro": "Those are ten bold technology predictions for the next decade. Which one do you think will happen first? Let me know in the comments. If you enjoyed thinking about the future, like and subscribe for more forward-looking tech content. See you in the future.",
    },
    {
        "title": "Top 10 Tech Gadgets Under $100 That Are Actually Worth Buying",
        "hook_text": "Best Tech Gadgets Under $100",
        "intro": "You do not need to spend a fortune to get great technology. These ten gadgets under one hundred dollars are carefully tested and actually improve your daily life. No junk, no gimmicks, just the best affordable tech you can buy right now.",
        "items": [
            ("10", "Anker Power Bank", "Anker's compact power banks deliver enough charge to fully recharge your phone twice. They are smaller than a wallet, support fast charging, and cost around thirty dollars. One of the most useful accessories you will ever own."),
            ("9", "TP-Link Smart Plug", "A smart plug lets you control any device with your voice or phone for under fifteen dollars. Set lights on timers, turn off appliances remotely, and save on electricity. It is the cheapest way to start building a smart home."),
            ("8", "Logitech M720 Mouse", "The Logitech M720 is a wireless mouse that works with up to three devices simultaneously. Switch between your laptop, tablet, and desktop with one button. It lasts two years on a single AA battery and costs under fifty dollars."),
            ("7", "Kasa Smart LED Bulb", "Kasa smart bulbs produce warm, adjustable light controlled from your phone. Set schedules, change colors, and dim without getting up. A four-pack costs less than a single dinner out and transforms your home's atmosphere."),
            ("6", "Blink Mini Camera", "The Blink Mini is an indoor security camera that costs just thirty-five dollars. It streams 1080p video, detects motion, and sends alerts to your phone. No subscription required for basic features."),
            ("5", "Sony MDR-7506 Headphones", "Sony's MDR-7506 are professional studio headphones that have been the industry standard for decades. They deliver crystal clear audio, are built to last forever, and cost under one hundred dollars. Used by musicians, podcasters, and audio engineers worldwide."),
            ("4", "Raspberry Pi 5", "The Raspberry Pi 5 is a fully functional computer the size of a credit card for about sixty dollars. You can use it to learn programming, build retro gaming consoles, run a home server, or automate your home. The possibilities are endless."),
            ("3", "Ulanzi Phone Tripod", "This compact tripod holds your phone steady for photos, videos, and video calls. It folds into a pocket-sized package and has wireless remote control. Essential for content creators and remote workers alike."),
            ("2", "FiiO E10K DAC", "The FiiO E10K is a USB DAC and headphone amplifier that dramatically improves your computer's audio quality. It drives high-impedance headphones and reduces noise from your motherboard. The cheapest upgrade that transforms your music listening experience."),
            ("1", "The Most Valuable Gadget Is Your Phone Case", "A good phone case is the most important gadget under one hundred dollars. It protects a device worth over one thousand dollars. A quality case from Spigen, Mous, or Casetify is the best investment in tech you can make."),
        ],
        "outro": "Those are the top 10 tech gadgets under one hundred dollars that are actually worth buying. How many do you own? Let me know which one is your favorite in the comments. If you found this helpful, like and subscribe for more tech recommendations. Thanks for watching.",
    },
]

TECH_FACTS = [
    "The first computer mouse was made of wood. Doug Engelbart invented it in 1964 and carved the casing from a block of wood. It had only one button.",
    "More computing power exists in a modern smartphone than NASA had when sending astronauts to the moon in 1969.",
    "Google processes over 8.5 billion searches every single day, according to publicly reported traffic estimates.",
    "The first commercial hard drive, the IBM 350, stored about five megabytes and was leased for roughly thirty-two hundred dollars per month in 1956.",
    "There are over one billion registered domain names on the internet, though only a fraction host actively maintained content.",
    "According to multiple studies, the average adult in developed countries spends around six to seven hours per day looking at screens.",
    "The original PlayStation was created as a CD-ROM add-on for the Super Nintendo. Nintendo backed out and Sony launched it as their own console.",
    "Python, one of the most popular programming languages, was named after the BBC comedy Monty Python's Flying Circus.",
    "The first domain name ever registered was symbolics.com on March 15, 1985. It was purchased by a computer manufacturer.",
    "The most expensive publicly confirmed domain name sale is voice.com, which sold for thirty million dollars in 2019.",
    "Amazon started as an online bookstore in Jeff Bezos' garage in 1994. The first book ever sold on Amazon was Fluid Concepts and Creative Analogies.",
    "The first iPhone had no copy and paste functionality. It took Apple two years and a software update to add this basic feature.",
    "YouTube was originally created as a video dating website called Tune In Hook Up before becoming the video-sharing platform we know.",
    "The QWERTY keyboard layout was created for the Sholes and Glidden typewriter in 1873. The layout spaced common letter pairs apart to reduce mechanical jams on early typewriters.",
    "Bitcoin's creator, Satoshi Nakamoto, has never been identified. Their identity remains one of the biggest mysteries in technology.",
    "The first webcam was created at Cambridge University to monitor a coffee pot. Researchers wanted to know when coffee was ready without leaving their desks.",
    "Nintendo was founded in 1889 as a playing card company. It did not enter the video game industry until the 1970s.",
    "The text content of Wikipedia compresses to well under 50 gigabytes. The sum of human knowledge documented on Wikipedia fits on a standard USB drive.",
    "In 1997, Philippe Kahn shared a picture of his newborn daughter in real time using a prototype camera phone he built himself, combining a digital camera with a mobile phone.",
    "Adobe's logo features a stylized letter A that was designed by the company's co-founder John Warnock's wife, Marva Warnock.",
    "The term computer bug was popularized by Grace Hopper in 1947 after finding an actual moth in a computer relay.",
    "The first computer virus for the wild was created in 1982 by a fifteen-year-old high school student named Rich Skrenta. It was called Elk Cloner.",
    "According to industry analysts, there are over seventeen billion connected IoT devices worldwide as of 2026, and the number continues to grow rapidly.",
    "Wi-Fi was originally going to be called IEEE 802.11b Direct Sequence Spread Spectrum. The name Wi-Fi was created by a branding consultancy and has no meaning.",
    "The first text message was sent in 1992 and said Merry Christmas. It was sent by a British engineer named Neil Papworth.",
    "Bluetooth is named after King Harald Bluetooth who united warring tribes in Scandinavia. The technology unites different devices.",
    "Kodak engineer Steven Sasson built the first self-contained digital camera in 1975. It weighed about eight pounds, captured 0.01 megapixel black-and-white images, and stored them on a cassette tape.",
    "SpaceX's Falcon 9 rocket can land itself after launch using autonomous control systems and deployable landing legs.",
    "Website loading speed directly affects sales. Amazon reportedly found that every one hundred milliseconds of delay could cost them one percent in sales, a figure widely cited in web performance research.",
    "The Google search algorithm uses over 200 factors to rank pages. The exact formula is a closely guarded secret that changes hundreds of times per year.",
    "The first hard disk drive to reach one terabyte was released by Hitachi in 2007. It contained five platters and ten read-write heads spinning at 7200 RPM.",
    "The first programmable computer, the Z3, was built by Konrad Zuse in 1941. It was destroyed during World War Two and rebuilt decades later.",
    "The Firefox logo is not a fox. It is a red panda. The original name was Phoenix but it was changed due to trademark issues.",
    "Linus Torvalds created Linux as a hobby project in 1991. He wrote in his famous email that he was doing it just for fun, not for profit.",
    "The first commercial 5G network launched in 2019. By 2026, approximately half of the world's population has access to 5G coverage, according to mobile industry reports.",
    "The most expensive smartphone ever produced is the Falcon Supernova iPhone 6 Pink Diamond edition, priced at over 48 million dollars.",
    "The amount of data created globally continues to accelerate rapidly, with recent years producing more data than all previous years combined.",
    "A Google search query uses a small amount of energy on their servers. Google has reported being carbon neutral since 2007 and continuously improves the energy efficiency of each search.",
    "In a 2023 laboratory test, researchers in Japan achieved a data transmission speed of 319 terabits per second using advanced fiber optic technology.",
    "Apple has over two billion active devices worldwide. More people own an Apple device than live in any single country except China and India.",
    "Bill Gates is one of the most followed individuals on LinkedIn, with tens of millions of followers. He regularly shares book recommendations and insights on global health and technology.",
    "The Motorola Atrix 4G in 2011 was one of the first major smartphones with a fingerprint scanner. Today, biometric security is standard on nearly every phone.",
    "NASA engineers spent years diagnosing and working around software issues in the Mars Rover Spirit mission, demonstrating the challenges of debugging code millions of miles away.",
    "The Samsung Galaxy Note 7 recall in 2016 cost the company over seventeen billion dollars in lost revenue and remains one of the most expensive product recalls in history.",
    "Tesla reports that its vehicles with Autopilot have driven billions of miles cumulatively. This real-world driving data is used to train the company's self-driving AI systems.",
    "The Unicode standard contains over 150,000 characters covering 168 modern and historic scripts. Every emoji you use is defined in Unicode.",
]


def _get_random_items(items, count):
    if len(items) <= count:
        return items[:]
    selected = random.sample(items, count)
    sorted_selected = sorted(selected, key=lambda x: items.index(x))
    return sorted_selected


def generate_tech_list():
    template = random.choice(TECH_LISTS)
    return _build_content(template)


def generate_tech_facts(fact_count=None):
    if fact_count is None:
        fact_count = random.randint(15, 25)
    selected = _get_random_items(TECH_FACTS, fact_count)
    items = []
    for i, fact in enumerate(selected, 1):
        short_title = fact[:60] + "..." if len(fact) > 60 else fact
        items.append((str(i), short_title, fact))
    title = f"{len(selected)} Mind-Blowing Tech Facts You Never Knew"
    hook_text = f"{len(selected)} Tech Facts"
    intro = "Technology is full of fascinating stories, surprising origins, and incredible statistics. Here are facts that will change how you see the devices and services you use every day."
    outro = "Which fact surprised you the most? Let me know in the comments below. If you learned something new, hit that like button and subscribe for more fascinating tech content. Thanks for watching."
    return _build_content({
        "format": "tech_facts",
        "title": title,
        "hook_text": hook_text,
        "intro": intro,
        "items": items,
        "outro": outro,
    })


CONTENT_FORMATS = ["tech_list", "tech_facts", "tutorial", "comparison", "case_study"]
SCRIPT_FORMATS = {"tutorial", "comparison", "case_study"}


def generate_script_content(format):
    candidates = [s for s in SCRIPT_TEMPLATES if s["format"] == format]
    if not candidates:
        candidates = SCRIPT_TEMPLATES
    template = random.choice(candidates)
    image_map = template["image_map"]
    script_parts = []
    built_segments = []
    for seg in template["segments"]:
        key = seg.get("title") or seg.get("heading") or ""
        seg_text = image_map.get(key, "")
        script_parts.append(seg_text)
        bs = {"type": seg["type"], "img": seg.get("img", "")}
        if seg["type"] == "intro":
            bs["text"] = seg.get("title", "")
            bs["detail"] = seg_text
        elif seg["type"] == "step":
            bs["step_num"] = seg["step_num"]
            bs["title"] = seg["title"]
            bs["text"] = seg_text
        elif seg["type"] == "comparison":
            bs["heading"] = seg["heading"]
            bs["text"] = seg_text
        elif seg["type"] == "result":
            bs["title"] = seg["title"]
            bs["text"] = seg_text
        elif seg["type"] == "outro":
            bs["text"] = seg_text
        built_segments.append(bs)
    return {
        "format": template["format"],
        "title": template["title"],
        "hook_text": template["hook_text"],
        "script": "\n\n".join(s for s in script_parts if s),
        "segments": built_segments,
        "tags": template.get("tags", []),
    }


def generate_content(format="random"):
    if format == "random":
        format = random.choice(CONTENT_FORMATS)
    if format in SCRIPT_FORMATS:
        return generate_script_content(format)
    if format == "tech_list":
        return generate_tech_list()
    elif format == "tech_facts":
        return generate_tech_facts()
    else:
        return generate_tech_list()


def _build_content(template):
    intro = template.get("intro", "")
    items = template.get("items", [])
    outro = template.get("outro", "")
    script_parts = []
    script_parts.append(intro)
    script_parts.append("")
    for num, title, description in items:
        if num:
            script_parts.append(f"Number {num}: {title}. {description}")
        else:
            script_parts.append(f"{title}. {description}")
        script_parts.append("")
    script_parts.append(outro)
    script = "\n".join(script_parts)
    segments = []
    segments.append({"type": "intro", "text": template.get("title", ""), "detail": intro})
    for num, title, description in items:
        segments.append({
            "type": "item",
            "number": num,
            "title": title,
            "summary": description,
            "source": "",
        })
    segments.append({"type": "outro", "text": outro})
    return {
        "format": template.get("format", "tech_list"),
        "title": template["title"],
        "hook_text": template.get("hook_text", ""),
        "script": script,
        "segments": segments,
    }
