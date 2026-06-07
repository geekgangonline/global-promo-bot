import os
import sqlalchemy
import datetime
from sqlalchemy import Column, VARCHAR, Integer, String, DateTime, ForeignKey, Boolean, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
from sqlalchemy.sql import exists
from dotenv import load_dotenv
load_dotenv()

SESSION_DURATION = os.getenv("SESSION_DURATION").split(" ")
drop_timer = int(SESSION_DURATION[0])
check_timer = int(SESSION_DURATION[1])
end_timer = int(SESSION_DURATION[2])

# assigns sqlite for local environment when debug is true and assigns remote heroku database when debug is false
DEBUG = (os.getenv("DEBUG") == 'True')
if DEBUG == True:
    SQLITE = 'sqlite:///database/database.db'
    engine = create_engine(SQLITE, connect_args={'check_same_thread': False})
if DEBUG == False:
    DATABASE_URL = os.getenv("DATABASE_URL")
    if DATABASE_URL==None:
        print("Cannot connect to heroku database check exposed vars of postgres setup")
    engine = create_engine(DATABASE_URL)



session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)
session = Session()
Base = declarative_base()

class Users(Base):
    """User class"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True)
    name = Column(String, nullable=False)
    username = Column(String)
    join_date = Column(DateTime)
    warns = Column(Integer)
    pool_count = Column(Integer)
    points = Column(Integer, default=0)
    blocked = Column(Boolean)
    lang = Column(String)
    email = Column(String)
    whop_id = Column(String)
    referral_code = Column(String)
    referred_by = Column(Integer)

    def __init__(self, user_id, name, username=None, join_date=None, warns=0, pool_count=0, points=0, blocked=False, lang="en", email=None, whop_id=None, referral_code=None, referred_by=None):
        self.user_id = user_id
        self.name = name
        self.lang = lang
        self.username = username
        self.join_date = join_date
        self.warns = warns
        self.pool_count = pool_count
        self.points = points
        self.blocked = blocked
        self.email = email
        self.whop_id = whop_id
        self.referral_code = referral_code
        self.referred_by = referred_by

    def commit(self):
        """commits query object to db"""
        session.add(self)
        session.commit()

    def warning(self):
        """increament warn by 1 everytime its called"""
        try:
            self.warns +=1
        except TypeError:
            self.warns = 1
        finally:
            if self.warns>=3:
                self.blocked=True
            session.commit()
            return self.warns
        
    # def blocked(self):
    #     if self.warns >= 3:
    #         return True
    #     else:
    #         return False
        
    def engaged(self):
        try:
            self.pool_count +=1
        except TypeError:
            self.pool_count=1
        finally:
            session.commit()
            return self.pool_count

    def add_points(self, amount=1):
        try:
            self.points += amount
        except TypeError:
            self.points = amount
        finally:
            session.commit()
            return self.points

    @classmethod
    def get(cls, userid):
        """retrive user from id"""
        user = session.query(cls).filter_by(user_id=userid).first()
        if user:
            return user
        else:
            return None

    @classmethod
    def get_username(cls, username):
        """retrive user from username"""
        user = session.query(cls).filter_by(username=username).first()
        if user:
            return user
        else:
            return None


    @classmethod
    def get_ids(cls):
        userall = session.query(cls).all()
        users = [i.user_id for i in userall]
        return users
    
    @classmethod
    def get_users(cls):
        userall = session.query(cls).all()
        users = [i for i in userall]
        return users

    @classmethod
    def create(cls, userid, name):
        """create new users by passing user id and name"""
        user = cls(
            user_id=userid,
            name=name
            )
        session.add(user)
        session.commit()
        return user

    @classmethod
    def delete_user(cls, userid):
        """retrive user from id"""
        user = session.query(cls).filter_by(user_id=userid).first()
        if user:
            session.delete(user)
            session.commit()
            return True
        else:
            return None

    def delete(self):
        """delete user object"""
        session.delete(self)
        session.commit()

    def __repr__(self):
        return f"User {self.name} {self.user_id}"

class Rounds(Base):
    __tablename__="rounds"
    id = Column(Integer, primary_key=True)
    start_time = Column(DateTime)
    post_link = Column(String)
    poster_user_id = Column(Integer)
    memberlist = relationship("MemberList", uselist=True, backref="round")

    def __init__(self, start_time, post_link=None, poster_user_id=None):
        """initializes rounds and set start time"""
        if type(start_time) == str:
            self.start_time = datetime.datetime.fromisoformat(start_time)
        else:
            self.start_time = start_time
        self.post_link = post_link
        self.poster_user_id = poster_user_id

    @classmethod
    def create(cls, start_time):
        """create round function by passing in time"""
        rounds = cls(
            start_time
            )
        session.add(rounds)
        session.commit()
        return rounds

    @classmethod
    def create_now(cls, post_link=None, poster_user_id=None):
        """create round function immediately"""
        start_time = datetime.datetime.now()
        rounds = cls(
            start_time,
            post_link=post_link,
            poster_user_id=poster_user_id
            )
        session.add(rounds)
        session.commit()
        return rounds

    def start(self):
        """retrieve the start time of round"""
        return self.start_time

    def check_time(self):
        t = self.end() - datetime.timedelta(minutes=check_timer)
        return t 

    def end(self):
        """retrieve the end time of round"""
        return self.start_time + datetime.timedelta(minutes=end_timer)

    def drop_duration(self):
        """returns time left time drop username period ends and returns false after it ends"""
        delta = self.start_time + datetime.timedelta(minutes=drop_timer)
        now = datetime.datetime.now()
        if now > delta:
            return False
        else:
            return (delta-now).seconds

    def join(self, user):
        """adds user to round by passing in the user object"""
        user_id = user.user_id
        # if MemberList.exist(user_id):
        #     self.memberlist
        #     return True
        # else:
        entry = MemberList(
            round_id=self.id,
            user=user
            )
        session.add(entry)
        session.commit()
    
    @classmethod
    def get_round(cls, id):
        """get round object by id"""
        return session.query(cls).filter_by(id=id).first()

    @classmethod
    def get_memberList(cls, id):
        """get list of all members in that round"""
        return session.query(MemberList).all()

    @classmethod
    def get_lastRound(cls):
        """get last round, or None if no rounds exist"""
        all_rounds = session.query(Rounds).all()
        return all_rounds[-1] if all_rounds else None

    @classmethod
    def get_all(cls):
        """get all rounds"""
        return session.query(Rounds).all()

    def commit(self):
        """add and commit session changes to db"""
        session.add(self)
        session.commit()

    def __repr__(self):
        """string representation of object"""
        return f"Round {self.id} {str(self.start_time)}"

class MemberList(Base):
    """member list class"""
    __tablename__="memberlist"
    id = Column(Integer, primary_key=True)
    round_id = Column(Integer, ForeignKey("rounds.id"))
    #userinfo
    user_id = Column(Integer)
    name = Column(String)
    username = Column(String)
    engaged = Column(Boolean, default=False)

    def __init__(self, round_id, user):
        self.round_id = round_id
        self.user_id = user.user_id
        self.name = user.name
        self.username = user.username
        self.engaged = False

    def mark_engaged(self):
        self.engaged = True
        session.commit()

    @classmethod
    def all(cls):
        return session.query(cls).all()

    @classmethod
    def exist(cls,user_id):
        """checks if user is on the list returns boolean"""
        return session.query(exists().where(cls.user_id==user_id)).scalar()

    @classmethod
    def get_unengaged_for_round(cls, round_id):
        return session.query(cls).filter(cls.round_id==round_id, cls.engaged==False).all()

    def __repr__(self):
        return f"MemberList {self.name} round{self.round_id}"


class SpinHistory(Base):
    """spin-to-win history"""
    __tablename__ = "spin_history"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    name = Column(String)
    prize = Column(String)
    spun_at = Column(DateTime, default=datetime.datetime.now)

    def __init__(self, user_id, name, prize):
        self.user_id = user_id
        self.name = name
        self.prize = prize
        self.spun_at = datetime.datetime.now()

    def commit(self):
        session.add(self)
        session.commit()

    @classmethod
    def last_spin(cls, user_id):
        return session.query(cls).filter_by(user_id=user_id).order_by(cls.id.desc()).first()

    @classmethod
    def total_spins(cls, user_id):
        return session.query(cls).filter_by(user_id=user_id).count()

    @classmethod
    def total_by_prize(cls, prize):
        return session.query(cls).filter_by(prize=prize).count()


class UserGroupRegistration(Base):
    """tracks which tier 2/3 groups a user has opted into"""
    __tablename__ = "user_group_registrations"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False)
    tier2_groups = Column(String)  # comma-separated group keys: "cypher,stream,thread"
    tier3_verified = Column(Boolean, default=False)

    def __init__(self, user_id, tier2_groups=None, tier3_verified=False):
        self.user_id = user_id
        self.tier2_groups = tier2_groups
        self.tier3_verified = tier3_verified

    def commit(self):
        session.add(self)
        session.commit()

    @classmethod
    def get(cls, user_id):
        return session.query(cls).filter_by(user_id=user_id).first()

    @classmethod
    def get_or_create(cls, user_id):
        obj = session.query(cls).filter_by(user_id=user_id).first()
        if not obj:
            obj = cls(user_id=user_id)
            session.add(obj)
            session.commit()
        return obj

    def has_tier2(self, group_key):
        if not self.tier2_groups:
            return False
        return group_key in self.tier2_groups.split(",")

    def add_tier2(self, group_key):
        current = set()
        if self.tier2_groups:
            current = set(self.tier2_groups.split(","))
        current.add(group_key)
        self.tier2_groups = ",".join(sorted(current))
        session.commit()

    def remove_tier2(self, group_key):
        if not self.tier2_groups:
            return
        current = set(self.tier2_groups.split(","))
        current.discard(group_key)
        self.tier2_groups = ",".join(sorted(current)) if current else None
        session.commit()


class GroupChat(Base):
    """tracks groups the bot is deployed in"""
    __tablename__ = "group_chats"
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, unique=True, nullable=False)
    title = Column(String)
    invite_link = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.now)

    def __init__(self, chat_id, title=None, invite_link=None):
        self.chat_id = chat_id
        self.title = title
        self.invite_link = invite_link

    def commit(self):
        session.add(self)
        session.commit()

    @classmethod
    def get(cls, chat_id):
        return session.query(cls).filter_by(chat_id=chat_id).first()

    @classmethod
    def all_groups(cls):
        return session.query(cls).all()

    @classmethod
    def all_member_ids(cls):
        """returns all user_ids registered in Users (all group members)"""
        return [u.user_id for u in session.query(Users.user_id).all()]


class PendingReferral(Base):
    """Persistent pending referral — survives bot restarts"""
    __tablename__ = "pending_referrals"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False)
    referrer_user_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now)

    def __init__(self, user_id, referrer_user_id):
        self.user_id = user_id
        self.referrer_user_id = referrer_user_id

    def commit(self):
        session.add(self)
        session.commit()

    @classmethod
    def consume(cls, user_id):
        ref = session.query(cls).filter_by(user_id=user_id).first()
        if ref:
            referrer_id = ref.referrer_user_id
            session.delete(ref)
            session.commit()
            return referrer_id
        return None


# ─── OPERATIONS MANAGEMENT TABLES ───────────────────────────────────────────

class TeamRole:
    OWNER = "owner"
    MANAGER = "manager"
    RECRUITER = "recruiter"
    SALES = "sales"
    CREATOR = "creator"

ROLE_HIERARCHY = {
    TeamRole.OWNER: 100,
    TeamRole.MANAGER: 80,
    TeamRole.RECRUITER: 50,
    TeamRole.SALES: 50,
    TeamRole.CREATOR: 10,
}

class Staff(Base):
    """Team members with role-based permissions"""
    __tablename__ = "staff"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False)
    name = Column(String)
    role = Column(String, default=TeamRole.CREATOR)
    telegram_handle = Column(String)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.now)

    def __init__(self, user_id, name, role=TeamRole.CREATOR, telegram_handle=None):
        self.user_id = user_id
        self.name = name
        self.role = role
        self.telegram_handle = telegram_handle

    def commit(self):
        session.add(self)
        session.commit()

    @classmethod
    def get(cls, user_id):
        return session.query(cls).filter_by(user_id=user_id).first()

    @classmethod
    def has_permission(cls, user_id, min_role=TeamRole.CREATOR):
        staff = cls.get(user_id)
        if not staff or not staff.active:
            return False
        return ROLE_HIERARCHY.get(staff.role, 0) >= ROLE_HIERARCHY.get(min_role, 0)


class Lead(Base):
    """Sales leads"""
    __tablename__ = "leads"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String)
    phone = Column(String)
    company = Column(String)
    source = Column(String)  # "ig_outreach", "email", "referral", "whop", "website"
    status = Column(String, default="new")  # new, contacted, qualified, proposal, closed_won, closed_lost
    notes = Column(String)
    assigned_to = Column(Integer)  # staff user_id
    estimated_value = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def __init__(self, name, email=None, phone=None, company=None, source=None, notes=None, assigned_to=None, estimated_value=0):
        self.name = name
        self.email = email
        self.phone = phone
        self.company = company
        self.source = source
        self.notes = notes
        self.assigned_to = assigned_to
        self.estimated_value = estimated_value

    def commit(self):
        session.add(self)
        session.commit()


class Client(Base):
    """Active clients"""
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String)
    phone = Column(String)
    company = Column(String)
    lead_id = Column(Integer)
    service = Column(String)
    monthly_value = Column(Integer, default=0)
    total_value = Column(Integer, default=0)
    status = Column(String, default="active")  # active, paused, completed, cancelled
    assigned_to = Column(Integer)
    created_at = Column(DateTime, default=datetime.datetime.now)

    def __init__(self, name, email=None, phone=None, company=None, lead_id=None, service=None, monthly_value=0, assigned_to=None):
        self.name = name
        self.email = email
        self.phone = phone
        self.company = company
        self.lead_id = lead_id
        self.service = service
        self.monthly_value = monthly_value
        self.assigned_to = assigned_to

    def commit(self):
        session.add(self)
        session.commit()


class Creator(Base):
    """UGC creators in the network"""
    __tablename__ = "creators"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    telegram_user_id = Column(Integer, unique=True)
    telegram_handle = Column(String)
    email = Column(String)
    city = Column(String)
    niches = Column(String)  # comma-separated
    instagram = Column(String)
    tiktok = Column(String)
    youtube = Column(String)
    audience_size = Column(Integer, default=0)
    past_campaigns = Column(Integer, default=0)
    total_earned = Column(Integer, default=0)
    status = Column(String, default="active")  # active, inactive, blacklisted
    rating = Column(Integer, default=3)  # 1-5
    created_at = Column(DateTime, default=datetime.datetime.now)

    def __init__(self, name, telegram_user_id=None, telegram_handle=None, email=None, instagram=None, niches=None):
        self.name = name
        self.telegram_user_id = telegram_user_id
        self.telegram_handle = telegram_handle
        self.email = email
        self.instagram = instagram
        self.niches = niches

    def commit(self):
        session.add(self)
        session.commit()

    @classmethod
    def get(cls, telegram_user_id):
        return session.query(cls).filter_by(telegram_user_id=telegram_user_id).first()


class Campaign(Base):
    """Marketing campaigns / assignments from brands"""
    __tablename__ = "campaigns"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    brand = Column(String)
    description = Column(String)
    payout = Column(Integer, default=0)
    slots_total = Column(Integer, default=1)
    slots_filled = Column(Integer, default=0)
    deadline = Column(DateTime)
    status = Column(String, default="open")  # open, in_progress, completed, cancelled
    type = Column(String)  # ugc, engagement, promotion, pr
    client_id = Column(Integer)
    created_at = Column(DateTime, default=datetime.datetime.now)

    def __init__(self, title, brand=None, description=None, payout=0, slots_total=1, deadline=None, type="ugc", client_id=None):
        self.title = title
        self.brand = brand
        self.description = description
        self.payout = payout
        self.slots_total = slots_total
        self.deadline = deadline
        self.type = type
        self.client_id = client_id

    def commit(self):
        session.add(self)
        session.commit()

    def slots_remaining(self):
        return self.slots_total - self.slots_filled


class Assignment(Base):
    """Individual creator assigned to a campaign slot"""
    __tablename__ = "assignments"
    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"))
    creator_id = Column(Integer, ForeignKey("creators.id"))
    status = Column(String, default="assigned")  # assigned, submitted, approved, paid, rejected
    submitted_url = Column(String)
    notes = Column(String)
    paid_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.datetime.now)

    def __init__(self, campaign_id, creator_id):
        self.campaign_id = campaign_id
        self.creator_id = creator_id

    def commit(self):
        session.add(self)
        session.commit()


class RevenueRecord(Base):
    """Revenue tracking"""
    __tablename__ = "revenue"
    id = Column(Integer, primary_key=True)
    amount = Column(Integer, nullable=False)
    source = Column(String)  # client_payment, whop_sub, upsell
    description = Column(String)
    client_id = Column(Integer)
    campaign_id = Column(Integer)
    recorded_by = Column(Integer)  # staff user_id
    recorded_at = Column(DateTime, default=datetime.datetime.now)

    def __init__(self, amount, source=None, description=None, client_id=None, campaign_id=None, recorded_by=None):
        self.amount = amount
        self.source = source
        self.description = description
        self.client_id = client_id
        self.campaign_id = campaign_id
        self.recorded_by = recorded_by

    def commit(self):
        session.add(self)
        session.commit()


class ActivityLog(Base):
    """Audit log for all operations"""
    __tablename__ = "activity_log"
    id = Column(Integer, primary_key=True)
    action = Column(String, nullable=False)
    entity_type = Column(String)  # lead, client, creator, campaign, assignment, revenue
    entity_id = Column(Integer)
    description = Column(String)
    performed_by = Column(Integer)  # staff user_id
    created_at = Column(DateTime, default=datetime.datetime.now)

    def __init__(self, action, entity_type=None, entity_id=None, description=None, performed_by=None):
        self.action = action
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.description = description
        self.performed_by = performed_by

    def commit(self):
        session.add(self)
        session.commit()

    @classmethod
    def log(cls, action, entity_type=None, entity_id=None, description=None, performed_by=None):
        entry = cls(action, entity_type, entity_id, description, performed_by)
        entry.commit()
        return entry


SERVICE_CATALOG = {
    "ugc_campaign": {"name": "UGC Campaign", "price": 500, "description": "User-generated content campaign with 10-20 creators"},
    "community_promo": {"name": "Community Promotion", "price": 750, "description": "Promote your brand across our 11-group network"},
    "pr_distribution": {"name": "PR Distribution", "price": 1000, "description": "Press release + distribution to music/fashion outlets"},
    "tv_placement": {"name": "TV Placement", "price": 2500, "description": "Television media placement and coverage"},
    "growth_package": {"name": "Full Growth Package", "price": 5000, "description": "UGC + Community + PR + TV bundled"},
    "clipfarm_access": {"name": "ClipFarm Access", "price": 47, "description": "Monthly access to clipping campaigns (per creator)"},
    "network_access": {"name": "Engagement Network", "price": 27, "description": "Monthly access to engagement groups (per artist)"},
    "bundle": {"name": "ClipFarm + Network Bundle", "price": 57, "description": "Both services bundled monthly"},
}


# Create all tables
Base.metadata.create_all(engine)

# migrations for existing tables
with engine.connect() as conn:
    for stmt in [
        "ALTER TABLE memberlist ADD COLUMN engaged BOOLEAN DEFAULT 0",
        "ALTER TABLE rounds ADD COLUMN post_link VARCHAR",
        "ALTER TABLE rounds ADD COLUMN poster_user_id INTEGER",
        "ALTER TABLE users ADD COLUMN points INTEGER DEFAULT 0",
        "ALTER TABLE users ADD COLUMN email VARCHAR",
        "ALTER TABLE users ADD COLUMN whop_id VARCHAR",
        "ALTER TABLE users ADD COLUMN referral_code VARCHAR",
        "ALTER TABLE users ADD COLUMN referred_by INTEGER",
        "ALTER TABLE user_group_registrations ADD COLUMN tier3_verified BOOLEAN DEFAULT 0",
        "ALTER TABLE users ADD COLUMN role VARCHAR DEFAULT 'creator'",
        "ALTER TABLE users ADD COLUMN phone VARCHAR",
        "ALTER TABLE users ADD COLUMN city VARCHAR",
        "ALTER TABLE users ADD COLUMN niches VARCHAR",
        "ALTER TABLE users ADD COLUMN audience_size INTEGER DEFAULT 0",
        "ALTER TABLE users ADD COLUMN total_earned INTEGER DEFAULT 0",
    ]:
        try:
            conn.execute(text(stmt))
        except:
            pass
    conn.commit()
