from typing import Optional

from sqlalchemy.exc import IntegrityError

from db.models import session_creator, Team, Members


class TeamService:
    @staticmethod
    def edit_team(name, project) -> bool:
        """Takes a name, and a project description"""
        # TODO: does this need a try/catch??
        session = session_creator()
        team = session.query(Team).filter(Team.team_name == name).first()
        if team is not None:
            team.project = project
            session.commit()
            session.close()
            return True
        else:
            session.commit()
            session.close()
            return False

    @staticmethod
    def get_team_by_name(name, session=None) -> Optional[Team]:
        """Returns the team with the given name, or none if it doesn't exist"""
        sess_flag = False
        if session is None:
            session = session_creator()
            sess_flag = True
        team = session.query(Team).filter(Team.team_name == name).first()
        if sess_flag:
            session.commit()
            session.close()
        return team

    @staticmethod
    def get_team_by_id(id, session=None) -> Optional[Team]:
        """Returns the team with the given id, or none if it doesn't exist"""
        sess_flag = False
        if session is None:
            session = session_creator()
            sess_flag = True
        team = session.query(Team).filter(Team.id == id).first()
        if sess_flag:
            session.commit()
            session.close()
        return team

    @staticmethod
    def get_teams_by_name(name, session=None) -> list:
        """Returns a list of teams that match the given name"""
        sess_flag = False
        if session is None:
            session = session_creator()
            sess_flag = True
        teams = session.query(Team).filter(Team.team_name.contains(name)).all()
        if sess_flag:
            session.commit()
            session.close()
        return teams

    @staticmethod
    def get_team_by_join_message_id(id, session=None) -> Optional[Team]:
        """Returns the team with the given join message id, or none if it doesn't exist"""
        sess_flag = False
        if session is None:
            session = session_creator()
            sess_flag = True
        team = session.query(Team).filter(Team.join_message_id == id).first()
        if sess_flag:
            session.commit()
            session.close()
        return team

    @staticmethod
    def get_teams_by_member(member, session=None) -> Optional[list]:
        """Returns a list of all teams the member is a part of"""
        sess_flag = False
        if session is None:
            session = session_creator()
            sess_flag = True
        team_ids = session.query(Members).filter(Members.member_id == str(member)).all()
        teams = []
        for t in team_ids:
            teams.append(session.query(Team).filter(Team.id == t.team_id).first())
        if sess_flag:
            session.commit()
            session.close()
        return teams

    @staticmethod
    def delete_team_by_name(name) -> bool:
        # TODO: Confirm that member references are deleted as well
        """Deletes team with given id"""
        session = session_creator()
        team = session.query(Team).filter(Team.team_name == name).first()
        if team is not None:
            # if team.members is not None:
            #     members = team.members
            #     for member in members:
            #         session.delete(member)
            session.delete(team)
            session.commit()
            session.close()
            return True
        else:
            session.commit()
            session.close()
            return False

    @staticmethod
    def get_all_teams(session=None) -> list:
        """Returns a list of team objects"""
        sess_flag = False
        if session is None:
            session = session_creator()
            sess_flag = True
        teams = session.query(Team).all()
        if sess_flag:
            session.commit()
            session.close()
        return teams

    @staticmethod
    def add_team(name, tc, join_message, project=None) -> bool:
        """Add a new team"""
        try:
            session = session_creator()
            session.add(
                Team(
                    team_name=name,
                    tc_id=tc,
                    join_message_id=join_message,
                    project=project,
                )
            )
            session.commit()
            session.close()
            return True
        except IntegrityError:
            return False

    @staticmethod
    def add_member(team, user_id, session=None):
        sess_flag = False
        if session is None:
            session = session_creator()
            sess_flag = True
        session.add(team)
        team.members.append(Members(member_id=user_id))
        if sess_flag:
            session.commit()
            session.close()

    @staticmethod
    def remove_member(team, user_id, session=None):
        sess_flag = False
        if session is None:
            session = session_creator()
            sess_flag = True
        session.add(team)
        session.query(Members).filter(
            Members.member_id == user_id, Members.team_id == team.id
        ).delete()
        if sess_flag:
            session.commit()
            session.close()
