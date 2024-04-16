from sqlalchemy import Table, ForeignKey, Column
from onereport.data.base import Base

personnel_report_rel = Table(
    "personnel_report_rel",
    Base.metadata,
    Column("report_id", ForeignKey("report.id"), primary_key=True),
    Column("personnel_id", ForeignKey("personnel.id"), primary_key=True),
)
