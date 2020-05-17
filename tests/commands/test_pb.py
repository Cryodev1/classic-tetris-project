from tests.helper import *

class GetPBCommandTestCase(CommandTestCase):
    with describe("discord"):
        def test_discord_with_no_user(self):
            self.expect_discord("!pb", [
                "User has not set a PB."
            ])

        def test_discord_with_no_pb(self):
            self.discord_user

            self.expect_discord("!pb", [
                "User has not set a PB."
            ])

        def test_discord_with_ntsc_pb(self):
            self.discord_user.user.add_pb(100000)

            self.expect_discord("!pb", [
                f"{self.discord_api_user.name} has an NTSC PB of 100,000."
            ])

        def test_discord_with_ntsc_18_and_19_pb(self):
            self.discord_user.user.add_pb(600000, starting_level=18)
            self.discord_user.user.add_pb(100000, starting_level=19)

            self.expect_discord("!pb", [
                f"{self.discord_api_user.name} has an NTSC PB of 600,000 (100,000 19 start)."
            ])

        def test_discord_with_pal_pb(self):
            self.discord_user.user.add_pb(100000, console_type="pal")

            self.expect_discord("!pb", [
                f"{self.discord_api_user.name} has a PAL PB of 100,000."
            ])

        def test_discord_with_ntsc_and_pal_pb(self):
            self.discord_user.user.add_pb(200000, console_type="ntsc")
            self.discord_user.user.add_pb(100000, console_type="pal")

            self.expect_discord("!pb", [
                f"{self.discord_api_user.name} has an NTSC PB of 200,000 and a PAL PB of 100,000."
            ])

        @patch("classic_tetris_project.commands.command.Command.any_platform_user_from_username",
               return_value=None)
        def test_discord_with_nonexistent_user(self, _):
            self.expect_discord("!pb Other User", [
                "User has not set a PB."
            ])

        @patch("classic_tetris_project.commands.command.Command.any_platform_user_from_username")
        def test_discord_with_user_with_no_pb(self, any_platform_user_from_username):
            discord_user = DiscordUserFactory(username="Other User")
            any_platform_user_from_username.return_value = discord_user

            self.expect_discord("!pb Other User", [
                "User has not set a PB."
            ])

            any_platform_user_from_username.assert_called_once_with("Other User")

        @patch("classic_tetris_project.commands.command.Command.any_platform_user_from_username")
        def test_discord_with_user_with_pb(self, any_platform_user_from_username):
            discord_user = DiscordUserFactory(username="Other User")
            discord_user.user.add_pb(100000)
            any_platform_user_from_username.return_value = discord_user

            self.expect_discord("!pb Other User", [
                "Other User has an NTSC PB of 100,000."
            ])

            any_platform_user_from_username.assert_called_once_with("Other User")

    with describe("twitch"):
        @patch.object(twitch.APIClient, "user_from_id",
                      lambda self, user_id, client=None: MockTwitchAPIUser.create(id=user_id))
        def test_twitch_with_no_user(self):
            self.expect_twitch("!pb", [
                "User has not set a PB."
            ])

        def test_twitch_with_no_pb(self):
            self.twitch_user

            self.expect_twitch("!pb", [
                "User has not set a PB."
            ])

        def test_twitch_with_ntsc_pb(self):
            self.twitch_user.user.add_pb(100000)

            self.expect_twitch("!pb", [
                f"{self.twitch_api_user.username} has an NTSC PB of 100,000."
            ])

        @patch("classic_tetris_project.commands.command.Command.any_platform_user_from_username",
               return_value=None)
        def test_twitch_with_nonexistent_user(self, _):
            self.expect_twitch("!pb other_user", [
                "User has not set a PB."
            ])

        @patch("classic_tetris_project.commands.command.Command.any_platform_user_from_username")
        def test_twitch_with_user_with_no_pb(self, any_platform_user_from_username):
            twitch_user = TwitchUserFactory(username="other_user")
            any_platform_user_from_username.return_value = twitch_user

            self.expect_twitch("!pb other_user", [
                "User has not set a PB."
            ])

            any_platform_user_from_username.assert_called_once_with("other_user")

        @patch("classic_tetris_project.commands.command.Command.any_platform_user_from_username")
        def test_twitch_with_user_with_pb(self, any_platform_user_from_username):
            twitch_user = TwitchUserFactory(username="other_user")
            twitch_user.user.add_pb(100000)
            any_platform_user_from_username.return_value = twitch_user

            self.expect_twitch("!pb other_user", [
                "other_user has an NTSC PB of 100,000."
            ])

            any_platform_user_from_username.assert_called_once_with("other_user")


class SetPBCommandTestCase(CommandTestCase):
    with describe("discord"):
        def test_discord_with_no_args(self):
            self.expect_discord("!setpb", [
                start_with("Usage:")
            ])

        def test_discord_with_no_user(self):
            self.expect_discord("!setpb 100,000", [
                f"<@{self.discord_api_user.id}> has a new NTSC PB of 100,000!"
            ])

            expect(User.objects.count()).to(equal(1))
            expect(ScorePB.objects.count()).to(equal(1))
            user = User.objects.last()
            expect(user.get_pb()).to(equal(100000))

        def test_discord_with_user(self):
            self.discord_user

            self.expect_discord("!setpb 100000", [
                f"<@{self.discord_api_user.id}> has a new NTSC PB of 100,000!"
            ])

            expect(User.objects.count()).to(equal(1))
            expect(ScorePB.objects.count()).to(equal(1))
            expect(self.discord_user.user.get_pb()).to(equal(100000))

        def test_discord_level(self):
            self.expect_discord("!setpb 100000 NTSC 19", [
                f"<@{self.discord_api_user.id}> has a new NTSC level 19 PB of 100,000!"
            ])

            expect(ScorePB.objects.count()).to(equal(1))
            expect(User.objects.last().get_pb(console_type="ntsc", starting_level=19)).to(equal(100000))

        def test_discord_pal(self):
            self.expect_discord("!setpb 100000 PAL", [
                f"<@{self.discord_api_user.id}> has a new PAL PB of 100,000!"
            ])

            expect(ScorePB.objects.count()).to(equal(1))
            expect(User.objects.last().get_pb(console_type="pal")).to(equal(100000))

        def test_discord_errors(self):
            self.expect_discord("!setpb asdf", [start_with("Usage:")])
            self.expect_discord("!setpb -5", ["Invalid PB."])
            self.expect_discord("!setpb 1500000", ["You wish, kid >.>"])
            self.expect_discord("!setpb 100000 NTSC -5", ["Invalid level."])
            self.expect_discord("!setpb 100000 NTSC 30", ["Invalid level."])
            self.expect_discord("!setpb 100000 foo", [start_with("Invalid PB type")])

    with describe("twitch"):
        def test_twitch_with_no_args(self):
            self.expect_twitch("!setpb", [
                start_with("Usage:")
            ])

        @patch.object(twitch.APIClient, "user_from_id",
                      lambda self, user_id, client=None: MockTwitchAPIUser.create(id=user_id))
        def test_twitch_with_no_user(self):
            self.twitch_channel
            expect(User.objects.count()).to(equal(1))

            self.expect_twitch("!setpb 100,000", [
                f"@{self.twitch_api_user.username} has a new NTSC PB of 100,000!"
            ])

            expect(User.objects.count()).to(equal(2))
            expect(ScorePB.objects.count()).to(equal(1))
            user = User.objects.last()
            expect(user.get_pb()).to(equal(100000))

        def test_twitch_with_user(self):
            self.twitch_channel
            self.twitch_user
            expect(User.objects.count()).to(equal(2))

            self.expect_twitch("!setpb 100000", [
                f"@{self.twitch_api_user.username} has a new NTSC PB of 100,000!"
            ])

            expect(User.objects.count()).to(equal(2))
            expect(ScorePB.objects.count()).to(equal(1))
            expect(self.twitch_user.user.get_pb()).to(equal(100000))
