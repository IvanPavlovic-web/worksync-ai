import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.database import Base


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


JSONType = JSON().with_variant(JSONB, "postgresql")
ArrayType = JSON().with_variant(ARRAY(String), "postgresql")


class User(Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str | None] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    profile: Mapped["Profile"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
    vault: Mapped["ProfileVault"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")


class Profile(Base):
    __tablename__ = "profiles"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    title: Mapped[str | None] = mapped_column(String(200)); summary: Mapped[str | None] = mapped_column(Text)
    seniority: Mapped[str | None] = mapped_column(String(40)); timezone: Mapped[str | None] = mapped_column(String(80))
    languages: Mapped[list | None] = mapped_column(JSONType); embedding: Mapped[list | None] = mapped_column(JSONType)
    user: Mapped[User] = relationship(back_populates="profile")
    experiences: Mapped[list["Experience"]] = relationship(cascade="all, delete-orphan", lazy="selectin")
    skills: Mapped[list["Skill"]] = relationship(cascade="all, delete-orphan", lazy="selectin")


class Experience(Base):
    __tablename__ = "experiences"
    id: Mapped[int] = mapped_column(primary_key=True); profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("profiles.id", ondelete="CASCADE"))
    company: Mapped[str] = mapped_column(String(200)); role: Mapped[str] = mapped_column(String(200))
    start_date: Mapped[datetime | None] = mapped_column(DateTime); end_date: Mapped[datetime | None] = mapped_column(DateTime)
    description: Mapped[str | None] = mapped_column(Text); technologies: Mapped[list | None] = mapped_column(JSONType)


class Skill(Base):
    __tablename__ = "skills"
    id: Mapped[int] = mapped_column(primary_key=True); profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("profiles.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(100)); category: Mapped[str | None] = mapped_column(String(60)); level: Mapped[str | None] = mapped_column(String(40)); years: Mapped[float | None] = mapped_column(Float)


class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = (UniqueConstraint("url", name="uq_jobs_url"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String(180), unique=True, index=True); source: Mapped[str] = mapped_column(String(100), index=True); source_ids: Mapped[list | None] = mapped_column(ArrayType)
    external_id: Mapped[str | None] = mapped_column(String(200)); title: Mapped[str] = mapped_column(String(300), index=True); company: Mapped[str] = mapped_column(String(250), index=True); url: Mapped[str] = mapped_column(String(2000))
    description: Mapped[str] = mapped_column(Text, default=""); location: Mapped[str] = mapped_column(String(250), default=""); city: Mapped[str | None] = mapped_column(String(120)); country_code: Mapped[str | None] = mapped_column(String(3), index=True)
    work_mode: Mapped[str] = mapped_column(String(30), default="onsite", index=True); category: Mapped[str | None] = mapped_column(String(80), index=True); seniority: Mapped[str | None] = mapped_column(String(40), index=True); employment_type: Mapped[str | None] = mapped_column(String(40)); language: Mapped[str | None] = mapped_column(String(30))
    salary_min: Mapped[float | None] = mapped_column(Float); salary_max: Mapped[float | None] = mapped_column(Float); currency: Mapped[str | None] = mapped_column(String(8)); salary_period: Mapped[str | None] = mapped_column(String(20))
    visa_sponsorship: Mapped[bool] = mapped_column(Boolean, default=False); housing_provided: Mapped[bool] = mapped_column(Boolean, default=False); relocation_support: Mapped[bool] = mapped_column(Boolean, default=False); meal_provided: Mapped[bool] = mapped_column(Boolean, default=False); allowed_countries: Mapped[list | None] = mapped_column(ArrayType); keywords: Mapped[list | None] = mapped_column(ArrayType)
    embedding: Mapped[list | None] = mapped_column(JSONType); is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True); views: Mapped[int] = mapped_column(Integer, default=0)
    posted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True)); expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True)); scraped_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc); seo_title: Mapped[str | None] = mapped_column(String(160)); seo_description: Mapped[str | None] = mapped_column(String(320))


class ProfileVault(Base):
    __tablename__ = "profile_vaults"
    id: Mapped[int] = mapped_column(primary_key=True); user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    first_name: Mapped[str | None] = mapped_column(String(100)); last_name: Mapped[str | None] = mapped_column(String(100)); email: Mapped[str | None] = mapped_column(String(320)); phone: Mapped[str | None] = mapped_column(String(50)); linkedin_url: Mapped[str | None] = mapped_column(String(500)); github_url: Mapped[str | None] = mapped_column(String(500)); portfolio_url: Mapped[str | None] = mapped_column(String(500)); twitter_url: Mapped[str | None] = mapped_column(String(500)); city: Mapped[str | None] = mapped_column(String(120)); country: Mapped[str | None] = mapped_column(String(120)); country_code: Mapped[str | None] = mapped_column(String(3)); postal_code: Mapped[str | None] = mapped_column(String(30)); state_region: Mapped[str | None] = mapped_column(String(120)); address_line1: Mapped[str | None] = mapped_column(String(250)); address_line2: Mapped[str | None] = mapped_column(String(250)); desired_salary: Mapped[str | None] = mapped_column(String(80)); notice_period_days: Mapped[int | None] = mapped_column(Integer); requires_sponsorship: Mapped[bool] = mapped_column(Boolean, default=False); willing_to_relocate: Mapped[bool] = mapped_column(Boolean, default=False); resume_url: Mapped[str | None] = mapped_column(String(1000)); custom_fields: Mapped[dict | None] = mapped_column(JSONType); gender: Mapped[str | None] = mapped_column(String(80)); veteran_status: Mapped[str | None] = mapped_column(String(80)); disability_status: Mapped[str | None] = mapped_column(String(80)); ethnicity: Mapped[str | None] = mapped_column(String(80))
    user: Mapped[User] = relationship(back_populates="vault")


class Application(Base):
    __tablename__ = "applications"
    id: Mapped[int] = mapped_column(primary_key=True); user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id")); job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("jobs.id")); status: Mapped[str] = mapped_column(String(40), default="saved"); cover_letter: Mapped[str | None] = mapped_column(Text); match_score: Mapped[float | None] = mapped_column(Float); applied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True)); created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc); updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)
    job: Mapped[Job] = relationship(lazy="joined")


class BlogPost(Base):
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(primary_key=True); slug: Mapped[str] = mapped_column(String(180), unique=True); locale: Mapped[str] = mapped_column(String(10), default="bs"); title: Mapped[str] = mapped_column(String(200)); excerpt: Mapped[str] = mapped_column(String(500), default=""); content_md: Mapped[str] = mapped_column(Text); content_html: Mapped[str] = mapped_column(Text); author: Mapped[str] = mapped_column(String(120)); category: Mapped[str] = mapped_column(String(80)); keywords: Mapped[list | None] = mapped_column(ArrayType); cover_image: Mapped[str | None] = mapped_column(String(1000)); seo_title: Mapped[str | None] = mapped_column(String(160)); seo_description: Mapped[str | None] = mapped_column(String(320)); published: Mapped[bool] = mapped_column(Boolean, default=False); views: Mapped[int] = mapped_column(Integer, default=0); published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc); updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)


