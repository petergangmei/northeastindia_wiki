import re
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone
from app.models import Content, Category, Tag, State, UserProfile

class Command(BaseCommand):
    help = 'Adds comprehensive Nagaland article with structured Wikipedia-style content'

    def handle(self, *args, **options):
        # Get or create admin user
        admin_user = self._get_or_create_admin()
        
        # Get or create necessary data
        categories = self._get_or_create_categories()
        tags = self._get_or_create_tags()
        nagaland_state = self._get_or_create_nagaland_state()
        
        # Check if Nagaland article already exists
        if Content.objects.filter(slug='nagaland').exists():
            self.stdout.write(self.style.WARNING("Nagaland article already exists. Skipping creation."))
            return
        
        # Create Nagaland article
        article = Content.objects.create(
            content_type='article',
            title="Nagaland",
            slug="nagaland",
            content=self._get_nagaland_content(),
            excerpt=self._get_nagaland_excerpt(),
            author=admin_user,
            published=True,
            published_at=timezone.now(),
            review_status='approved',
            meta_description="Nagaland is a state in the north-eastern region of India, known for its rich tribal culture, diverse ethnic groups, and the famous Hornbill Festival.",
            references=self._get_nagaland_references()
        )
        
        # Add categories, tags, and states
        article.categories.add(
            categories['Geography'],
            categories['History'],
            categories['Culture'],
            categories['States']
        )
        
        article.tags.add(
            tags['Nagaland'],
            tags['Northeast India'],
            tags['Seven Sisters'],
            tags['Tribal Culture'],
            tags['British India'],
            tags['Independence'],
            tags['Insurgency'],
            tags['Hornbill Festival'],
            tags['Kohima'],
            tags['Naga People']
        )
        
        article.states.add(nagaland_state)
        
        # Create initial revision
        ArticleRevision.objects.create(
            article=article,
            user=admin_user,
            content=article.content,
            comment="Initial creation of comprehensive Nagaland article"
        )
        
        self.stdout.write(self.style.SUCCESS(f"Successfully created Nagaland article with ID: {article.id}"))
        self.stdout.write(self.style.SUCCESS(f"Article URL: /articles/nagaland/"))

    def _get_or_create_admin(self):
        """Get or create an admin user for authoring articles"""
        try:
            admin = User.objects.get(username='admin')
        except User.DoesNotExist:
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@northeastindia.wiki',
                password='admin123'
            )
            UserProfile.objects.create(
                user=admin,
                role='admin',
                bio='Northeast India Wiki Administrator',
                location='Northeast India',
                website='https://northeastindia.wiki'
            )
            self.stdout.write(self.style.SUCCESS("Created admin user"))
        return admin

    def _get_or_create_categories(self):
        """Get or create categories for the article"""
        categories_data = [
            {'name': 'Geography', 'description': 'Geographical information about Northeast India'},
            {'name': 'History', 'description': 'Historical events and periods'},
            {'name': 'Culture', 'description': 'Cultural aspects of Northeast India'},
            {'name': 'States', 'description': 'Information about Northeast Indian states'},
            {'name': 'Politics', 'description': 'Political information and governance'},
        ]
        
        categories = {}
        for cat_data in categories_data:
            cat, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'slug': slugify(cat_data['name']),
                    'description': cat_data['description']
                }
            )
            categories[cat_data['name']] = cat
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created category: {cat.name}"))
        
        return categories

    def _get_or_create_tags(self):
        """Get or create tags for the article"""
        tag_names = [
            'Nagaland', 'Northeast India', 'Seven Sisters', 'Tribal Culture',
            'British India', 'Independence', 'Insurgency', 'Hornbill Festival',
            'Kohima', 'Naga People', 'Dimapur', 'World War II', 'Battle of Kohima',
            'Zapu Phizo', 'Statehood', 'Ethnic Groups', 'Traditional Culture'
        ]
        
        tags = {}
        for tag_name in tag_names:
            tag, created = Tag.objects.get_or_create(
                name=tag_name,
                defaults={'slug': slugify(tag_name)}
            )
            tags[tag_name] = tag
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created tag: {tag.name}"))
        
        return tags

    def _get_or_create_nagaland_state(self):
        """Get or create Nagaland state"""
        state, created = State.objects.get_or_create(
            name='Nagaland',
            defaults={
                'slug': 'nagaland',
                'description': 'Known for Hornbill Festival and tribal heritage',
                'capital': 'Kohima',
                'formation_date': timezone.datetime(1963, 12, 1).date(),
                'population': 1980602,  # 2011 Census
                'area': 16579,  # sq km
                'languages': 'English, Angami, Ao, Sumi, Lotha, Konyak'
            }
        )
        
        # If state already exists, update it with comprehensive data
        if not created:
            state.description = 'Known for Hornbill Festival and tribal heritage'
            state.capital = 'Kohima'
            state.formation_date = timezone.datetime(1963, 12, 1).date()
            state.population = 1980602  # 2011 Census
            state.area = 16579  # sq km
            state.languages = 'English, Angami, Ao, Sumi, Lotha, Konyak'
            state.save()
            self.stdout.write(self.style.SUCCESS(f"Updated state: {state.name}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Created state: {state.name}"))
        return state

    def _get_nagaland_excerpt(self):
        """Get the article excerpt"""
        return """Nagaland (/ˈnɑːɡəlænd/) is a state in the north-eastern region of India. It is bordered by the Indian states of Arunachal Pradesh to the north, Assam to the west, Manipur to the south, and the Naga Self-Administered Zone of the Sagaing Region of Myanmar (Burma) to the east. Its capital city is Kohima and its largest city is the twin Chümoukedima–Dimapur. The state has an area of 16,579 square kilometres (6,401 sq mi) with a population of 1,980,602 as per the 2011 Census of India, making it one of the least populated states in India."""

    def _get_nagaland_content(self):
        """Get the full structured content for Nagaland article"""
        return """
<p><strong>Nagaland</strong> (<a href="#" title="Help:IPA/English">/ˈnɑːɡəlænd/</a>) is a <a href="#" title="States and union territories of India">state</a> in the <a href="#" title="Northeast India">north-eastern region</a> of <a href="#" title="India">India</a>. It is bordered by the Indian states of <a href="#" title="Arunachal Pradesh">Arunachal Pradesh</a> to the north, <a href="#" title="Assam">Assam</a> to the west, <a href="#" title="Manipur">Manipur</a> to the south, and the <a href="#" title="Naga Self-Administered Zone">Naga Self-Administered Zone</a> of the <a href="#" title="Sagaing Region">Sagaing Region</a> of <a href="#" title="Myanmar">Myanmar (Burma)</a> to the east. Its capital city is <a href="#" title="Kohima">Kohima</a> and its largest city is the twin <a href="#" title="Chümoukedima">Chümoukedima</a>–<a href="#" title="Dimapur">Dimapur</a>. The state has an area of 16,579 square kilometres (6,401 sq mi) with a population of 1,980,602 as per the <a href="#" title="2011 Census of India">2011 Census of India</a>, making it one of the least populated states in India.</p>

<p>Nagaland consists of 17 administrative districts, inhabited by 17 major tribes along with other sub-tribes. Each tribe is distinct in character from the other in terms of customs, language and dress. It is a land of <a href="#" title="Folklore">folklore</a> passed down the generations through word of mouth. The earliest recorded history of the Nagas of the present-day Nagaland dates back to the 13th century.</p>

<p>In the 19th century, the <a href="#" title="British India">British India</a> forces began expanding their influence in Northeast India, including the <a href="#" title="Naga Hills">Naga Hills</a>. After India's independence in 1947, the question of the Naga Hills' political status emerged. Nagaland was a district in the <a href="#" title="State of Assam">State of Assam</a> until 1957, known to others as "The Naga Hills". The <a href="#" title="Naga National Council">Naga National Council</a>, led by <a href="#" title="Zapu Phizo">Zapu Phizo</a>, demanded an independent Naga state and launched an armed insurgency. The <a href="#" title="Indian Government">Indian Government</a>, however, maintained that Nagaland was an integral part of the <a href="#" title="Indian Union">Indian Union</a>. The conflict between the Naga National Council and the Indian Government resulted in a protracted insurgency. The State of Nagaland was formally inaugurated on 1 December 1963, as the 16th state of the Indian Union, and a democratically elected government took office in 1964.</p>

<p>Nagaland is home to a rich variety of natural, cultural, and environmental resources. It is a mountainous state and lies between the parallels of 95° and 94° eastern longitude and 25.2° and 27.0° latitude north. The high-profile <a href="#" title="Dzüko Valley">Dzüko Valley</a> is at <a href="#" title="Viswema">Viswema</a>, in the southern region of the state. The state has significant resources of natural minerals, petroleum, and hydropower, with the <a href="#" title="Primary sector">primary sector</a> which is mostly agriculture still accounting for 24.6% of its economy. Other significant activities include forestry, tourism, insurance, real estate, horticulture, and miscellaneous <a href="#" title="Cottage industry">cottage industries</a>.</p>

<h2>Etymology</h2>

<p>The origin of the word 'Naga' is unclear. The present day Naga people have historically been referred to by many names, like "Noga" or "Naka" by the inhabitants of the <a href="#" title="Ahom kingdom">Ahom kingdom</a> in what is now considered as <a href="#" title="Assam">Assam</a> which means "naked", "Hao" by <a href="#" title="Meitei people">Meitei people</a> of <a href="#" title="Imphal Valley">Imphal Valley</a> and "Nakas" or 'Naga' by <a href="#" title="Burmese people">Burmese</a> of what is now considered as <a href="#" title="Myanmar">Myanmar</a> meaning "people with earrings", while others suggest it means pierced noses. Eventually, Nakanchi or Naganchi came to be an endonym for the region. In recent years, some cultural activists have called for the state to be renamed Naganchi.</p>

<p>Before the arrival of <a href="#" title="European colonialism">European colonialism</a> in South Asia, there had been many wars, persecution and raids from <a href="#" title="Burma">Burma</a> on the Nagas, <a href="#" title="Meitei people">Meiteis</a> and others in India's northeast. The invaders came for "head hunting" and to seek wealth and captives from these tribes and ethnic groups. When the British inquired with Burmese guides about the people living in the northern Himalayas, they were told 'Naka'. This was recorded as 'Naga' and has been in use thereafter.</p>

<h2>History</h2>

<p><em>Main article: <a href="#" title="History of the Nagas">History of the Nagas</a></em><br>
<em>See also: <a href="#" title="Naga people">Naga people</a></em></p>

<p>The ancient history of the Nagas is unclear. Ethnic groups migrated at different times, each settling in the northeastern part of present India and establishing their respective sovereign mountain terrains and village states. There are no records of whether they came from the northern Mongolian region, southeast Asia, or southwest China, except that their origins are from the east of India, and historical records show the present-day Naga people settled before the arrival of the <a href="#" title="Ahom people">Ahoms</a> in 1228 CE.</p>

<h3>Mongkawng</h3>

<p>According to the Burmese chronicles <em>Tagung Yazawin</em>, the first <a href="#" title="Chaopha">Chaopha</a> of <a href="#" title="Mongkawng">Mongkawng</a> Samlongpha (1150–1201 CE) with the main town in <a href="#" title="Mogaung">Mogaung</a> captured Naga country in the early 1200s. In the chronicle Naga country is named as "Khang Se".</p>

<h3>Kingdom of Mongmao</h3>

<p>According to the <em>History of Hsenwi</em> state chronicle and <em>Mengguo Zhanbi</em>, in 1318, Si Kefa, the ruler of <a href="#" title="Mongmao">Mongmao</a> appointed his brother Sanlongfa as the general and led an army of 90,000 to attack the king of Mong Wehsali Long (Assam). In the end, he designed a plan to make Mong Wehsali Long surrender and pay tribute every 3 years. Hkum Sam Long accepted the terms made by the ministers of Mong Wehsali Long and marched back to Mongmao.</p>

<h3>Kingdom of Ava</h3>

<p>In Yan-aung-myin Pagoda inscription found in <a href="#" title="Pinya">Pinya</a> of Myanmar mentions that the <a href="#" title="Kingdom of Ava">Kingdom of Ava</a> under <a href="#" title="Minkhaung I">Minkhaung I</a> (1400–1421) in the early 1400s extended till the territories of the Nagas.</p>

<h3>British administration</h3>

<p>With the arrival of the <a href="#" title="British East India Company">British East India Company</a> in the early 19th century, followed by the <a href="#" title="British Raj">British Raj</a>, Britain expanded its domain over the whole of South Asia, including the Naga Hills. The first Europeans to enter the hills were Captain Francis Jenkins and Lieutenant Robert Pemberton in 1832. The early contact with the Naga ethnic groups was characterised by suspicion and conflict. The colonial interests in Assam, such as managers of tea estates and other trading posts led defensive action against raids from the ethnic groups who were known for their bravery and "head hunting" practices. To put an end to these raids, the British troops recorded 10 military expeditions between 1839 and 1850. In February 1851, at the bloody Battle of Kikrüma, people died on both the British side and the Kikrüma (Naga) side; in the days after the battle, inter-ethnic warfare followed that led to more bloodshed. After that war, the British adopted a policy of caution and non-interference with Naga ethnic groups.</p>

<p>Despite this, colonists continued to move into Naga peoples' territory. Between 1851 and 1865, Naga ethnic groups continued to raid the British in Assam. The British India Government took over the holdings of the East Indian Company following the <a href="#" title="Indian Rebellion of 1857">Indian Rebellion of 1857</a>. The failings and atrocities of the East Indian Company led the British Crown to review its governance structure throughout South Asia including its northeastern region. In 1866, the British India administration established a post at Samaguting with the explicit goal of ending intertribal warfare and tribal raids on property and personnel.</p>

<p>In 1869, Captain Butler was appointed to lead and consolidate the British presence in the Nagaland Hills. In 1878, the headquarters were transferred to <a href="#" title="Kohima">Kohima</a> — creating a city that remains an important center of administration, commerce, and culture for Nagaland.</p>

<p>On 4 October 1879, British political agent G. H. Damant went to <a href="#" title="Khonoma">Khonoma</a> with troops, where he was shot dead with 35 of his team. Kohima was subsequently attacked and the stockade looted. This violence led to a determined effort by the British Raj to return and respond. The subsequent defeat of Khonoma marked the end of serious and persistent ultimatums in the Naga Hills.</p>

<p>Between 1880 and 1922, the British administration consolidated their position over a large area of the Naga Hills and integrated it into its Assam operations. The British administration enforced the rupee as the currency for economic activity and a system of structured ethnic government that was very different from historic social governance practices.</p>

<p>In parallel, since the mid-19th century, Christian missionaries from the United States and Europe, stationed in India, reached into Nagaland and neighbouring states, converting Nagaland's Naga ethnic groups from animism to Christianity.</p>

<h3>World War II</h3>

<p><em>Main article: <a href="#" title="Battle of Kohima">Battle of Kohima</a></em><br>
<em>See also: <a href="#" title="Battle of the Tennis Court">Battle of the Tennis Court</a></em></p>

<p>In 1944, during <a href="#" title="World War II">World War II</a>, the <a href="#" title="Japanese Army">Japanese Army</a>, with the help of the <a href="#" title="Indian National Army">Indian National Army</a> led by <a href="#" title="Netaji Subhash Chandra Bose">Netaji Subhashchandra Bose</a>, invaded through Burma and attempted to take India through Kohima. The population was evacuated. British India soldiers defended the area of Kohima and having lost many of their original force were relieved by British in June 1944. Together the British and Indian troops successfully repelled the Japanese troops. The battle was fought from 4 April to 22 June 1944 from the town of Kohima, coordinated with action at <a href="#" title="Imphal">Imphal</a>, <a href="#" title="Manipur">Manipur</a>. The Indian National Army lost half their numbers, many through starvation, and were forced to withdraw through Burma.</p>

<p>There is the <a href="#" title="Kohima War Cemetery">World War II Cemetery</a>, and the War Museum, in honour of those who died during World War II during the fighting between the British Empire and Japanese troops. Nearly 4,000 British Empire troops died, along with 3,000 Japanese. Many of those who died were Naga people, particularly the <a href="#" title="Angami people">Angami Nagas</a>. Near the memorial is the Kohima Cathedral, on Aradura Hill, built with funds from the families and friends of deceased Japanese soldiers. Prayers are held in Kohima for peace and in memory of the fallen of both sides of the battle.</p>

<h3>Naga national awakening</h3>

<p>In 1929, a memorandum was submitted to the <a href="#" title="Simon Commission">Simon Statutory Commission</a>, requesting that the Nagas be exempt from reforms and new taxes proposed in British India, and should be left alone to determine their own future.</p>

<p>The Naga Memorandum submitted by the <a href="#" title="Naga Club">Naga Club</a> (which later became the <a href="#" title="Naga National Council">Naga National Council</a>) to the Simon Commission explicitly stated, 'to leave us alone to determine ourselves as in ancient times.'</p>

<h3>Post-independence history</h3>

<p>After the independence of India in 1947, the area remained a part of the province of Assam. Nationalist activities arose among a section of the Nagas. Phizo-led Naga National Council demanded a political union of their ancestral and native groups. The movement led to a series of violent incidents, that damaged government and civil infrastructure, attacked government officials and civilians. The central government sent the <a href="#" title="Indian Army">Indian Army</a> in 1955, to restore order. In 1957, an agreement was reached between Naga leaders and the Indian government, creating a single separate region of the Naga Hills. The <a href="#" title="Tuensang">Tuensang</a> frontier was united with this single political region, <a href="#" title="Naga Hills Tuensang Area">Naga Hills Tuensang Area</a> (NHTA), and it became an autonomous area under <a href="#" title="Sixth Schedule to the Constitution of India">Sixth Schedule to the Constitution of India</a>. It was to be "administered by the Governor as the agent of the President but will be distinct from the North East Frontier Administration".</p>

<p>This was not satisfactory to the Nagas, however, and agitation with violence increased across the state – including attacks on army and government institutions, banks, as well as non-payment of taxes. In July 1960, following discussion between Prime Minister <a href="#" title="Jawaharlal Nehru">Nehru</a> and the leaders of the <a href="#" title="Naga People Convention">Naga People Convention</a> (NPC), a 16-point agreement was arrived at whereby the Government of India recognised the formation of Nagaland as a full-fledged state within the Union of India.</p>

<h3>Nagaland statehood and late 20th century</h3>

<p>Accordingly, the territory was placed under the <em>Nagaland Transitional Provisions Regulation, 1961</em> which provided for an Interim body consisting of 45 members to be elected by tribes according to the customs, traditions and usage of the respective tribes. Subsequently, Nagaland attained statehood with the enactment of the <em>state of Nagaland Act in 1962</em> by the Parliament. The interim body was dissolved on 30 November 1963 and the state of Nagaland was formally inaugurated on 1 December 1963 and Kohima was declared as the state capital. After elections in January 1964, the first democratically elected <a href="#" title="Nagaland Legislative Assembly">Nagaland Legislative Assembly</a> was constituted on 11 February 1964.</p>

<p>The rebel activity continued in many Naga inhabited areas both in India and Burma. Ceasefires were announced and negotiations continued, but this did little to stop the violence. In March 1975, a direct presidential rule was imposed by the then Prime Minister <a href="#" title="Indira Gandhi">Indira Gandhi</a> on the state. In November 1975, some leaders of the largest rebel groups agreed to lay down their arms and accept the Indian constitution, a small group did not agree and continued their insurgent activity. The <a href="#" title="Nagaland Baptist Church Council">Nagaland Baptist Church Council</a> played an important role by initiating peace efforts in the 1960s.</p>

<h3>21st century</h3>

<p>In 2004, two powerful bombs were set off on the same day and struck the <a href="#" title="Dimapur Railway Station">Dimapur Railway Station</a> and the Hong Kong Market, resulting in 30 deaths and wounding over 100 others in the deadliest terrorist attack in Nagaland to date.</p>

<p>Over the 5-year period of 2009 to 2013, between 0 and 11 civilians died per year in Nagaland from rebellion related activity (or less than 1 death per 100,000 people), and between 3 and 55 militants died per year in inter-factional killings (or between 0 and 3 deaths per 100,000 people).</p>

<p>In early 2017, Nagaland went into a state of civil unrest and protests in response to the announcement to implement 33% women's reservation in the Civic Elections.</p>

<p>On 4 December 2021, a unit of the 21st Para Special Forces of the Indian Army killed six civilian labourers near <a href="#" title="Oting Village">Oting Village</a> in the <a href="#" title="Mon District">Mon District</a> of Nagaland. Eight more civilians and a soldier were killed in subsequent violence. The incident was widely condemned, with many calling out to repeal and revoke the <a href="#" title="Armed Forces Special Powers Act">Armed Forces Special Powers Act</a>.</p>

<p>The most recent <a href="#" title="Nagaland Legislative Assembly election">Nagaland Legislative Assembly election</a> took place on 27 February 2023 to elect the Members of the Legislative Assembly (MLA) in the 60 Assembly Constituencies in the state. A voter turnout of 87% was observed in the election. The election created history by electing two women candidates for the first time in Nagaland — <a href="#" title="Hekani Jakhalu Kense">Hekani Jakhalu Kense</a> and <a href="#" title="Salhoutuonuo Kruse">Salhoutuonuo Kruse</a>. Both candidates were from the ruling <a href="#" title="Nationalist Democratic Progressive Party">Nationalist Democratic Progressive Party</a> (NDPP). Salhoutuonuo Kruse later became the first woman minister of the Nagaland Legislative Assembly.</p>

<h2>Geography</h2>

<p>Nagaland is largely a mountainous state. The <a href="#" title="Naga Hills">Naga Hills</a> rise from the <a href="#" title="Brahmaputra Valley">Brahmaputra Valley</a> in <a href="#" title="Assam">Assam</a> to about 610 metres (2,000 ft) and rise further to the southeast, as high as 1,800 metres (5,900 ft). <a href="#" title="Mount Saramati">Mount Saramati</a> is the highest peak at 3,826 metres (12,552 ft) and its range forms the border with <a href="#" title="Myanmar">Myanmar</a>. These ranges are part of a complex mountain system, and the parts of the mountain ranges in Nagaland are called the Naga Hills.</p>

<p>The state is home to a rich variety of flora and fauna. About one-sixth of Nagaland is under the forest cover. The state has a <a href="#" title="Monsoon">monsoon</a> climate with high humidity levels. Annual rainfall averages around 1,800–2,500 millimetres (70–100 in), concentrated in the months of May to September. Temperatures range from 21 to 40 °C (70 to 104 °F). In winter, temperatures do not generally drop below 4 °C (39 °F), but frost is common at high elevations.</p>

<h2>Demographics</h2>

<p>As per the <a href="#" title="2011 Census of India">2011 Census of India</a>, Nagaland has a population of 1,980,602 with 1,025,707 males and 954,895 females, a <a href="#" title="Sex ratio">sex ratio</a> of 931 females per 1000 males. The <a href="#" title="Decadal growth rate">decadal growth rate</a> was 0.6%. The density of population is 119 per km<sup>2</sup>. The literacy rate of the state was 80.11%, with the male literacy rate at 83.29% and female literacy rate at 76.69%.</p>

<p>Nagaland is home to 17 major tribes: <a href="#" title="Angami people">Angami</a>, <a href="#" title="Ao people">Ao</a>, <a href="#" title="Chakhesang people">Chakhesang</a>, <a href="#" title="Chang people">Chang</a>, <a href="#" title="Dimasa people">Dimasa</a>, <a href="#" title="Kachari people">Kachari</a>, <a href="#" title="Konyak people">Konyak</a>, <a href="#" title="Kuki people">Kuki</a>, <a href="#" title="Lotha people">Lotha</a>, <a href="#" title="Phom people">Phom</a>, <a href="#" title="Pochury people">Pochury</a>, <a href="#" title="Rengma people">Rengma</a>, <a href="#" title="Sangtam people">Sangtam</a>, <a href="#" title="Sumi people">Sumi</a>, <a href="#" title="Tikhir people">Tikhir</a>, <a href="#" title="Yimchunger people">Yimchunger</a>, and <a href="#" title="Zeliang people">Zeliang</a>, along with other sub-tribes. Each of these tribes has its distinct customs, language, and traditions.</p>

<h2>Government and politics</h2>

<p>Nagaland became the 16th state of India on 1 December 1963. The state has a unicameral legislature. The <a href="#" title="Nagaland Legislative Assembly">Nagaland Legislative Assembly</a> has 60 seats, out of which 59 are for <a href="#" title="Scheduled Tribes">scheduled tribes</a> and one seat is open for all. The state sends one representative each to the <a href="#" title="Lok Sabha">Lok Sabha</a> and the <a href="#" title="Rajya Sabha">Rajya Sabha</a> of the Indian Parliament.</p>

<p>The Governor is the constitutional head of state, appointed by the <a href="#" title="President of India">President of India</a>. The Chief Minister is the head of government and is appointed by the Governor. The Council of Ministers is appointed by the Governor on the advice of the Chief Minister.</p>

<h2>Economy</h2>

<p>Agriculture is the most important economic activity in Nagaland, with over 70% of the population dependent on it. <a href="#" title="Rice">Rice</a> is the staple food, and it is the most widely cultivated crop. Other important crops include <a href="#" title="Maize">maize</a>, <a href="#" title="Millet">millet</a>, <a href="#" title="Sugarcane">sugarcane</a>, <a href="#" title="Potato">potato</a>, and <a href="#" title="Pulses">pulses</a>. <a href="#" title="Jhum cultivation">Jhum cultivation</a> (shifting cultivation) is widely practiced.</p>

<p>The state has significant resources of natural minerals, <a href="#" title="Petroleum">petroleum</a>, and <a href="#" title="Hydropower">hydropower</a>. The <a href="#" title="Primary sector of the economy">primary sector</a>, which is mostly agriculture, still accounts for 24.6% of the state's <a href="#" title="Gross State Domestic Product">GSDP</a>. Other significant activities include forestry, tourism, insurance, real estate, horticulture, and miscellaneous <a href="#" title="Cottage industry">cottage industries</a>.</p>

<h2>Culture</h2>

<p>Nagaland is known for its rich cultural heritage. The <a href="#" title="Hornbill Festival">Hornbill Festival</a>, held annually in December, is the most famous cultural event. It showcases the traditional arts, crafts, sports, food, and customs of the Naga tribes. The festival is named after the <a href="#" title="Great hornbill">Great Hornbill</a>, which is the most revered bird for the Naga people.</p>

<p>Traditional <a href="#" title="Naga cuisine">Naga cuisine</a> is characterized by the use of <a href="#" title="Chili pepper">chili peppers</a>, <a href="#" title="Ginger">ginger</a>, <a href="#" title="Garlic">garlic</a>, and <a href="#" title="Fermented soybean">fermented soybean</a>. Pork, beef, chicken, and fish are the main sources of protein. <a href="#" title="Smoked meat">Smoked meat</a> and dried fish are popular, as they can be stored for longer periods.</p>

<p>Each Naga tribe has its traditional attire, which is woven with intricate designs and bright colors. The traditional dresses are worn during festivals and special occasions. <a href="#" title="Naga shawl">Naga shawls</a> are particularly famous for their beauty and craftsmanship.</p>

<p>Music and dance are integral parts of Naga culture. Traditional songs often narrate the legends and history of the tribes. Folk dances are performed during festivals and celebrations, each having its unique steps and significance.</p>
        """

    def _get_nagaland_references(self):
        """Get references for the article"""
        return """[1] Census of India 2011: Provisional Population Totals – Nagaland
[2] Government of Nagaland Official Website
[3] Singh, K.S. (ed.) (1995). Communities, Segments, Synonyms, Surnames and Titles. Anthropological Survey of India. Oxford University Press. 
[4] Ao, Temsula (2003). These Hills Called Home: Stories from a War Zone. Zubaan Books.
[5] Iralu, Kaka D. (2000). Nagaland and India: The Blood and the Tears. Kaka D. Iralu.
[6] Chasie, Charles (1999). The Naga Imbroglio: A Personal Perspective. United Publishers.
[7] Misra, Sanghamitra (2000). Becoming a Borderland: The Politics of Space and Identity in Colonial Northeastern India. Routledge.
[8] Government of India, Ministry of Development of North Eastern Region
[9] Nagaland State Human Development Report 2004
[10] Statistical Handbook of Nagaland 2018
[11] Nagaland Tourism Department Official Records
[12] Battle of Kohima Archives, Imperial War Museums
[13] Northeast India Development Finance Corporation Ltd. Reports
[14] Economic Survey of Nagaland, Various Years
[15] Hornbill Festival Documentation, Government of Nagaland
[16] Naga Cultural Studies, Nagaland University Publications
[17] Tribal Research Institute, Government of Nagaland
[18] Indian Archaeological Survey Records on Nagaland
[19] British Colonial Records on Naga Hills Administration
[20] Nagaland Legislative Assembly Records"""

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting Nagaland article creation...'))
        
        # Get or create admin user
        admin_user = self._get_or_create_admin()
        
        # Get or create necessary data
        categories = self._get_or_create_categories()
        tags = self._get_or_create_tags()
        nagaland_state = self._get_or_create_nagaland_state()
        
        # Check if Nagaland article already exists
        if Content.objects.filter(slug='nagaland').exists():
            self.stdout.write(self.style.WARNING("Nagaland article already exists. Skipping creation."))
            return
        
        # Create Nagaland article
        article = Content.objects.create(
            content_type='article',
            title="Nagaland",
            slug="nagaland",
            content=self._get_nagaland_content(),
            excerpt=self._get_nagaland_excerpt(),
            author=admin_user,
            published=True,
            published_at=timezone.now(),
            review_status='approved',
            meta_description="Nagaland is a state in the north-eastern region of India, known for its rich tribal culture, diverse ethnic groups, and the famous Hornbill Festival.",
            references=self._get_nagaland_references()
        )
        
        # Add categories, tags, and states
        article.categories.add(
            categories['Geography'],
            categories['History'],
            categories['Culture'],
            categories['States']
        )
        
        article.tags.add(
            tags['Nagaland'],
            tags['Northeast India'],
            tags['Seven Sisters'],
            tags['Tribal Culture'],
            tags['British India'],
            tags['Independence'],
            tags['Insurgency'],
            tags['Hornbill Festival'],
            tags['Kohima'],
            tags['Naga People']
        )
        
        article.states.add(nagaland_state)
        
        # Create initial revision
        try:
            ArticleRevision.objects.create(
                article=article,
                user=admin_user,
                content=article.content,
                comment="Initial creation of comprehensive Nagaland article"
            )
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Could not create revision: {e}"))
        
        self.stdout.write(self.style.SUCCESS(f"Successfully created Nagaland article with ID: {article.id}"))
        self.stdout.write(self.style.SUCCESS(f"Article URL: /articles/nagaland/"))