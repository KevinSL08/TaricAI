from sqlalchemy import Column, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.database import Base


class Section(Base):
    """21 secciones TARIC (I-XXI)."""

    __tablename__ = "sections"

    id = Column(Integer, primary_key=True)
    roman_numeral = Column(String(10), unique=True, nullable=False)  # I, II, ... XXI
    title_es = Column(Text, nullable=False)
    title_en = Column(Text)
    notes = Column(Text)

    chapters = relationship("Chapter", back_populates="section")


class Chapter(Base):
    """Capítulos TARIC (2 dígitos: 01-99)."""

    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True)
    code = Column(String(2), unique=True, nullable=False)  # "01" - "99"
    description_es = Column(Text, nullable=False)
    description_en = Column(Text)
    notes = Column(Text)
    section_id = Column(Integer, ForeignKey("sections.id"), nullable=False)

    section = relationship("Section", back_populates="chapters")
    headings = relationship("Heading", back_populates="chapter")

    __table_args__ = (Index("ix_chapters_code", "code"),)


class Heading(Base):
    """Partidas TARIC (4 dígitos: 0101-9999)."""

    __tablename__ = "headings"

    id = Column(Integer, primary_key=True)
    code = Column(String(4), unique=True, nullable=False)  # "0101"
    description_es = Column(Text, nullable=False)
    description_en = Column(Text)
    notes = Column(Text)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=False)

    chapter = relationship("Chapter", back_populates="headings")
    subheadings = relationship("Subheading", back_populates="heading")

    __table_args__ = (Index("ix_headings_code", "code"),)


class Subheading(Base):
    """Subpartidas SA (6 dígitos: 010121-999999)."""

    __tablename__ = "subheadings"

    id = Column(Integer, primary_key=True)
    code = Column(String(6), unique=True, nullable=False)  # "010121"
    description_es = Column(Text, nullable=False)
    description_en = Column(Text)
    notes = Column(Text)
    duty_rate = Column(String(50))  # e.g. "0%", "7.5%", "12.8% + 27.5 EUR/100 kg"
    heading_id = Column(Integer, ForeignKey("headings.id"), nullable=False)

    heading = relationship("Heading", back_populates="subheadings")
    taric_codes = relationship("TaricCode", back_populates="subheading")

    __table_args__ = (Index("ix_subheadings_code", "code"),)


class TaricCode(Base):
    """Códigos TARIC completos (10 dígitos)."""

    __tablename__ = "taric_codes"

    id = Column(Integer, primary_key=True)
    code = Column(String(10), unique=True, nullable=False)  # "0101210000"
    description_es = Column(Text, nullable=False)
    description_en = Column(Text)
    notes = Column(Text)
    duty_rate = Column(String(50))
    supplementary_unit = Column(String(20))  # e.g. "kg", "p/st", "l"
    subheading_id = Column(Integer, ForeignKey("subheadings.id"), nullable=False)

    subheading = relationship("Subheading", back_populates="taric_codes")

    __table_args__ = (Index("ix_taric_codes_code", "code"),)
