init python:
    class KiwiiComment:
        def __init__(
            self,
            user: Union[PlayableCharacter, NonPlayableCharacter],
            message: str,
            number_likes: int = random.randint(250, 500),
            mentions: Optional[list[Union[NonPlayableCharacter, PlayableCharacter]]] = None,
        ):
            self.user = user
            self.message = message
            self.number_likes = number_likes

            self.mentions = mentions if mentions is not None else []

            self.liked = False
            self._replies: list[KiwiiReply] = []
            self.reply: Optional[KiwiiReply] = None

        @property
        def replies(self):
            try:
                self._replies
            except AttributeError:
                self._replies = []

            return self._replies

        @replies.setter
        def replies(self, value: list["KiwiiReply"]):
            self._replies = value


    class KiwiiReply(KiwiiComment):
        def __init__(
            self,
            message: str,
            func: Optional[Callable[[KiwiiPost], None]] = None,
            number_likes: int = random.randint(250, 500),
            mentions: Optional[list[Union[NonPlayableCharacter, PlayableCharacter]]] = None,
        ):
            super().__init__(mc, message, number_likes, mentions)
            self.func = func


    class KiwiiPost:
        def __init__(
            self,
            user: Union[PlayableCharacter, NonPlayableCharacter],
            image: str,
            message: str = "",
            mentions: Optional[list[Union[NonPlayableCharacter, PlayableCharacter]]] = None,
            number_likes: int = random.randint(250, 500),
        ):
            self.user = user
            self.image = f"images/{image}"
            self.message = message
            self.mentions = mentions if mentions is not None else []

            self.number_likes = number_likes

            self.liked = False

            self.sent_comments: list[KiwiiComment] = []
            self.pending_comments: list[KiwiiComment] = []

            kiwii_posts.append(self)

            kiwii.unlock()

        @property
        def username(self):
            return self.user.username

        @property
        def profile_picture(self):
            return self.user.profile_picture

        @property
        def replies(self) -> list[KiwiiReply]:
            try:
                return self.sent_comments[-1].replies
            except (AttributeError, IndexError):
                return []

        def new_comment(
            self,
            user: Union[PlayableCharacter, NonPlayableCharacter],
            message: str,
            number_likes: int = random.randint(250, 500),
            mentions: Optional[list[Union[NonPlayableCharacter, PlayableCharacter]]] = None,
        ):
            comment = KiwiiComment(user, message, number_likes, mentions)

            # Add message to queue
            if self.replies:
                self.pending_comments.append(comment)
            else:
                self.sent_comments.append(comment)

            kiwii.notification = True
            return comment

        def add_reply(
            self,
            content: str,
            func: Optional[Callable[[KiwiiPost], None]] = None,
            number_likes: int = random.randint(250, 500),
            mentions: Optional[list[Union[NonPlayableCharacter, PlayableCharacter]]] = None,
        ):
            reply = KiwiiReply(content, func, number_likes, mentions)

            # Append reply to last sent message
            if self.pending_comments:
                self.pending_comments[-1].replies.append(reply)
            elif self.sent_comments:
                self.sent_comments[-1].replies.append(reply)
            else:
                message = self.new_comment(mc, "")
                message.replies.append(reply)

            kiwii.notification = True
            return reply

        def selected_reply(self, reply: KiwiiReply):
            self.sent_comments.append(
                KiwiiComment(mc, reply.message, reply.number_likes, reply.mentions)
            )
            self.sent_comments[-1].reply = reply
            self.sent_comments[-1].replies = []

            # Run reply function
            if reply.func is not None:
                try:
                    reply.func(self)
                except TypeError:
                    reply.func()  # type: ignore
                reply.func = None

            # Send next queued message(s)
            try:
                while not self.replies:
                    self.sent_comments.append(self.pending_comments.pop(0))
            except IndexError:
                pass

        def remove_post(self):
            if self in kiwii_posts:
                kiwii_posts.remove(self)
            del self

        # Backwards compatibility.
        def newComment(
            self,
            user: NonPlayableCharacter,
            message: str,
            number_likes: int = random.randint(250, 500),
            mentions: Optional[list[Union[NonPlayableCharacter, PlayableCharacter]]] = None,
        ):
            return self.new_comment(user, message, number_likes, mentions)

        def addReply(
            self,
            message: str,
            func: Optional[Callable[["KiwiiPost"], None]] = None,
            number_likes: int = random.randint(250, 500),
            mentions: Optional[list[Union[NonPlayableCharacter, PlayableCharacter]]] = None,
        ):
            return self.add_reply(message, func, number_likes, mentions)

        def selectedReply(self, reply: KiwiiReply):
            return self.selected_reply(reply)


    def get_total_likes():
        return sum(post.numberLikes for post in kiwii_posts if post.user == mc) + sum(
            comment.numberLikes
            for post in kiwii_posts
            for comment in post.sent_comments
            if comment.user == mc
        )


    def find_kiwii_post(image: Optional[str] = None, message: Optional[str] = None):
        for post in kiwii_posts:
            if post.image == image:
                return post
            if post.message == message:
                return post


screen kiwii_base():
    modal True

    default image_path = "images/phone/kiwii/app-assets/"

    use base_phone:
        frame:
            background image_path + "background.webp"

            transclude

            hbox:
                ysize 72
                xalign 0.5
                ypos 843
                spacing 45

                imagebutton:
                    idle image_path + "home-button-idle.webp"
                    hover image_path + "home-button-hover.webp"
                    action Show("kiwii_home")
                    yalign 0.5

                null width 25

                null width 45

                imagebutton:
                    idle image_path + "liked-button-idle.webp"
                    hover image_path + "liked-button-hover.webp"
                    action Show("kiwii_home", posts=list(filter(lambda post: post.liked, kiwii_posts)))
                    yalign 0.5

                imagebutton:
                    idle Transform(mc.profile_picture, xysize=(30, 30))
                    action Show("kiwii_preferences")
                    yalign 0.5


screen kiwii_preferences():
    tag phone_tag
    modal True

    default profile_pictures_index = 0
    $ mc.profile_picture = mc.profile_pictures[profile_pictures_index]

    use kiwii_base:
        vbox:
            xalign 0.5
            ypos 175
            spacing 25

            vbox:
                xalign 0.5
                spacing 5

                add Transform(mc.profile_picture, xysize=(200, 200)) xalign 0.5

                hbox:
                    spacing 50
                    xalign 0.5

                    textbutton "<":
                        if profile_pictures_index > 0:
                            action SetScreenVariable("profile_pictures_index", profile_pictures_index - 1)
                        text_style "kiwii_PrefTextButton"

                    textbutton ">":
                        if profile_pictures_index + 1 < len(mc.profile_pictures):
                            action SetScreenVariable("profile_pictures_index", profile_pictures_index + 1)
                        text_style "kiwii_PrefTextButton"

            vbox:
                xalign 0.5

                text "Username:" style "kiwii_ProfileName" xalign 0.5
                input:
                    value FieldInputValue(mc, "username")
                    default mc.username
                    length 15
                    color "#006400"
                    outlines [ (absolute(0), "#000", absolute(0), absolute(0)) ]
                    xalign 0.5

            vbox:
                xalign 0.5

                text "Total Likes:" style "kiwii_ProfileName" at truecenter
                text str(get_total_likes()) at truecenter:
                    color "#006400"
                    outlines [ (absolute(0), "#000", absolute(0), absolute(0)) ]


screen kiwii_home(posts=kiwii_posts):
    tag phone_tag

    default image_path = "images/phone/kiwii/app-assets/"

    $ kiwii.notification = False

    use kiwii_base:

        viewport:
            mousewheel True
            draggable True
            ypos 152
            ysize 692

            vbox:
                xalign 0.5
                xsize 416

                null height 20

                for post in reversed(posts):
                    frame:
                        xalign 0.5
                        xsize 386
                        padding (10, 10)

                        has vbox

                        hbox:
                            xsize 366

                            hbox:
                                spacing 10

                                add Transform(post.profile_picture, xysize=(55, 55))
                                text post.username style "kiwii_ProfileName" yalign 0.5

                            hbox:
                                spacing 5
                                align (1.0, 0.5)

                                add image_path + "static-button-1.webp"
                                add image_path + "static-button-2.webp"

                        null height 10

                        vbox:
                            spacing 5

                            imagebutton:
                                idle Transform(post.image, xysize=(366, 206))
                                action Show("kiwii_image", img=post.image)
                                xalign 0.5
                            text Kiwii.get_message(post) style "kiwii_CommentText" xalign 0.5

                        null height 10

                        hbox:
                            xsize 366

                            hbox:
                                imagebutton:
                                    idle image_path + "like.webp"
                                    hover image_path + "like-press.webp"
                                    selected_idle image_path + "like-press.webp"
                                    selected post.liked
                                    action Function(Kiwii.toggle_liked, post)

                                text "{}".format(post.numberLikes) style "kiwii_LikeCounter" yalign 0.5

                            imagebutton:
                                idle image_path + "comment.webp"
                                hover image_path + "commenthover.webp"
                                action Show("kiwiiPost", post=post)
                                xalign 1.0

    if config_debug:
        for post in reversed(posts):
            if post.replies:
                timer 0.1 action Show("kiwiiPost", post=post)
        
        if not any(post.replies for post in reversed(posts)):
            timer 0.1:
                if renpy.get_screen("free_roam"):
                    action [Hide("tutorial"), Hide("phone"), Hide("message_reply")]
                else:
                    action [Hide("tutorial"), Hide("message_reply"), Return()]


screen kiwiiPost(post):
    tag phone_tag
    zorder 200

    default image_path = "/images/phone/kiwii/app-assets/"

    use kiwii_base:
        imagebutton:
            idle Transform(post.image, xysize=(416, 234))
            action Show("kiwii_image", img=post.image)
            xalign 0.5
            ypos 152
            
        viewport:
            mousewheel True
            draggable True
            xysize (357, 400)
            pos (20, 386)

            vbox:
                spacing 20

                null

                for comment in post.sent_comments:
                    if comment.message.strip():
                        vbox:
                            spacing 5

                            hbox:
                                spacing 10

                                add Transform(comment.user.profile_picture, xysize=(55, 55))
                                text comment.user.username style "kiwii_ProfileName" yalign 0.5

                            text Kiwii.get_message(comment) style "kiwii_CommentText"

                            hbox:
                                spacing 5

                                imagebutton:
                                    idle image_path + "like.webp"
                                    hover image_path + "like-press.webp"
                                    selected_idle image_path + "like-press.webp"
                                    selected comment.liked
                                    action Function(Kiwii.toggle_liked, comment)
                                text "[comment.numberLikes]" style "kiwii_LikeCounter" yalign 0.5

    if post.replies:
        vbox:
            xpos 1200
            yalign 0.84
            spacing 15

            for reply in post.replies:
                textbutton reply.message:
                    text_style "kiwii_ReplyText"
                    style "kiwii_reply"
                    action Function(post.selectedReply, reply)

    if config_debug:
        if post.replies:
            $ reply = renpy.random.choice(post.replies)
            timer 0.1 repeat True action Function(post.selectedReply, reply)
        else:
            timer 0.1:
                if renpy.get_screen("free_roam"):
                    action [Hide("tutorial"), Hide("phone"), Hide("message_reply")]
                else:
                    action [Hide("tutorial"), Hide("message_reply"), Return()]


screen kiwii_image(img):
    zorder 100
    modal True

    imagebutton:
        idle Transform(img, zoom=0.85)
        action Hide("kiwii_image")
        align (0.5, 0.5)