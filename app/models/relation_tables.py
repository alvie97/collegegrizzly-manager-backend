from app import db

# college relationships
college_major = db.Table(
    "college_major",
    db.Column("college_id", db.Integer, db.ForeignKey("college.id")),
    db.Column("major_id", db.Integer, db.ForeignKey("major.id")))

college_state = db.Table(
    "college_state",
    db.Column("college_id", db.Integer, db.ForeignKey("college.id")),
    db.Column("state_id", db.Integer, db.ForeignKey("state.id")))

college_county = db.Table(
    "college_county",
    db.Column("college_id", db.Integer, db.ForeignKey("college.id")),
    db.Column("county_id", db.Integer, db.ForeignKey("county.id")))

college_place = db.Table(
    "college_place",
    db.Column("college_id", db.Integer, db.ForeignKey("college.id")),
    db.Column("place_id", db.Integer, db.ForeignKey("place.id")))

college_consolidated_city = db.Table(
    "college_consolidated_city",
    db.Column("college_id", db.Integer, db.ForeignKey("college.id")),
    db.Column("consolidated_city_id", db.Integer,
              db.ForeignKey("consolidated_city.id")))

# scholarship relationships

scholarships_needed = db.Table(
    "scholarships_needed",
    db.Column("needs_id", db.Integer, db.ForeignKey("scholarship.id")),
    db.Column("needed_id", db.Integer, db.ForeignKey("scholarship.id")))
scholarship_ethnicity = db.Table(
    "scholarship_ethnicity",
    db.Column("scholarship_id", db.Integer, db.ForeignKey("scholarship.id")),
    db.Column("ethnicity_id", db.Integer, db.ForeignKey("ethnicity.id")))
scholarship_program = db.Table(
    "scholarship_program",
    db.Column("scholarship_id", db.Integer, db.ForeignKey("scholarship.id")),
    db.Column("program_id", db.Integer, db.ForeignKey("program.id")))

scholarship_state = db.Table(
    "scholarship_state",
    db.Column("scholarship_id", db.Integer, db.ForeignKey("scholarship.id")),
    db.Column("state_id", db.Integer, db.ForeignKey("state.id")))

scholarship_county = db.Table(
    "scholarship_county",
    db.Column("scholarship_id", db.Integer, db.ForeignKey("scholarship.id")),
    db.Column("county_id", db.Integer, db.ForeignKey("county.id")))

scholarship_place = db.Table(
    "scholarship_place",
    db.Column("scholarship_id", db.Integer, db.ForeignKey("scholarship.id")),
    db.Column("place_id", db.Integer, db.ForeignKey("place.id")))

scholarship_consolidated_city = db.Table(
    "scholarship_consolidated_city",
    db.Column("scholarship_id", db.Integer, db.ForeignKey("scholarship.id")),
    db.Column("consolidated_city_id", db.Integer,
              db.ForeignKey("consolidated_city.id")))
