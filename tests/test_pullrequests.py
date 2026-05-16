"""Tests for pull request models and PullRequestClient."""

from unittest.mock import MagicMock

import pytest

from conftest import PR_COMMENT_SPEC, PR_THREAD_SPEC, ok_response

from ez_ados.git.pullrequests.clients import PullRequestClient
from ez_ados.git.pullrequests.enums import CommentTypeEnum, ThreadStatusEnum, VoteEnum
from ez_ados.git.pullrequests.models import (
    IdentityRefCreate,
    IdentityRefWithVote,
    IdentityRefWithVoteCollection,
    PullRequestThread,
    PullRequestThreadCollection,
    PullRequestThreadComment,
    PullRequestThreadCommentCreate,
    PullRequestThreadCreate,
)
from ez_ados.identities.clients import IdentityClient

# ---------------------------------------------------------------------------
# Enums: parametrized validate()
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "value, expected",
    [
        ("unknown", CommentTypeEnum.unknown),
        ("text", CommentTypeEnum.text),
        ("codeChange", CommentTypeEnum.codeChange),
        ("system", CommentTypeEnum.system),
        (0, CommentTypeEnum.unknown),
        (1, CommentTypeEnum.text),
    ],
)
def test_comment_type_enum_validate(value, expected):
    assert CommentTypeEnum.validate(value) == expected


@pytest.mark.parametrize("bad", ["bad_value", 99])
def test_comment_type_enum_invalid(bad):
    with pytest.raises(ValueError):
        CommentTypeEnum.validate(bad)


@pytest.mark.parametrize(
    "value, expected",
    [
        ("unknown", ThreadStatusEnum.unknown),
        ("active", ThreadStatusEnum.active),
        ("fixed", ThreadStatusEnum.fixed),
        ("wontFix", ThreadStatusEnum.wontFix),
        ("closed", ThreadStatusEnum.closed),
        ("byDesign", ThreadStatusEnum.byDesign),
        ("pending", ThreadStatusEnum.pending),
        (0, ThreadStatusEnum.unknown),
        (4, ThreadStatusEnum.closed),
    ],
)
def test_thread_status_enum_validate(value, expected):
    assert ThreadStatusEnum.validate(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        ("rejected", VoteEnum.rejected),
        ("waitingForAuthor", VoteEnum.waitingForAuthor),
        ("noVote", VoteEnum.noVote),
        ("approvedWithSuggestions", VoteEnum.approvedWithSuggestions),
        ("approved", VoteEnum.approved),
        (-10, VoteEnum.rejected),
        (-5, VoteEnum.waitingForAuthor),
        (0, VoteEnum.noVote),
        (5, VoteEnum.approvedWithSuggestions),
        (10, VoteEnum.approved),
    ],
)
def test_vote_enum_validate(value, expected):
    assert VoteEnum.validate(value) == expected


@pytest.mark.parametrize("bad", ["maybe", 99])
def test_vote_enum_invalid(bad):
    with pytest.raises(ValueError):
        VoteEnum.validate(bad)


# ---------------------------------------------------------------------------
# PullRequestThreadCommentCreate
# ---------------------------------------------------------------------------


def test_pr_thread_comment_create_minimal():
    c = PullRequestThreadCommentCreate(content="hello")
    assert c.content == "hello"
    assert c.comment_type == CommentTypeEnum.system


def test_pr_thread_comment_create_explicit_type():
    c = PullRequestThreadCommentCreate(content="hi", commentType="text")
    assert c.comment_type == CommentTypeEnum.text


# ---------------------------------------------------------------------------
# PullRequestThreadComment
# ---------------------------------------------------------------------------


def test_pr_thread_comment_valid():
    c = PullRequestThreadComment.model_validate(PR_COMMENT_SPEC)
    assert c.id == 1
    assert c.content == "hello"
    assert c.comment_type == CommentTypeEnum.text


# ---------------------------------------------------------------------------
# PullRequestThreadCreate
# ---------------------------------------------------------------------------


def test_pr_thread_create_minimal():
    thread = PullRequestThreadCreate(comments=[PullRequestThreadCommentCreate(content="A comment")])
    assert len(thread.comments) == 1
    assert thread.status is None
    assert thread.properties == {}


def test_pr_thread_create_with_status():
    thread = PullRequestThreadCreate(
        comments=[PullRequestThreadCommentCreate(content="note")],
        status="active",
    )
    assert thread.status == ThreadStatusEnum.active


# ---------------------------------------------------------------------------
# PullRequestThread
# ---------------------------------------------------------------------------


def test_pr_thread_valid():
    thread = PullRequestThread.model_validate(PR_THREAD_SPEC)
    assert thread.id == 10
    assert thread.deleted is False
    assert len(thread.comments) == 1


def test_pr_thread_deleted_alias():
    spec = {**PR_THREAD_SPEC, "isDeleted": True}
    thread = PullRequestThread.model_validate(spec)
    assert thread.deleted is True


def test_pr_thread_with_properties():
    spec = {
        **PR_THREAD_SPEC,
        "properties": {"tfci.plan": {"$type": "System.String", "$value": "my-plan"}},
    }
    thread = PullRequestThread.model_validate(spec)
    assert thread.properties is not None
    assert thread.properties["tfci.plan"].value == "my-plan"


def test_pr_thread_collection():
    data = {"value": [PR_THREAD_SPEC]}
    col = PullRequestThreadCollection.model_validate(data)
    assert col.count == 1


# ---------------------------------------------------------------------------
# IdentityRefWithVote
# ---------------------------------------------------------------------------


def test_identity_ref_with_vote_defaults():
    ref = IdentityRefWithVote.model_validate({"id": "user-1"})
    assert ref.id == "user-1"
    assert ref.vote == VoteEnum.noVote
    assert ref.display_name is None


def test_identity_ref_with_vote_full():
    ref = IdentityRefWithVote.model_validate(
        {
            "id": "user-1",
            "displayName": "Alice",
            "uniqueName": "alice@example.com",
            "vote": 10,
            "isRequired": True,
        }
    )
    assert ref.display_name == "Alice"
    assert ref.vote == VoteEnum.approved
    assert ref.is_required is True


def test_identity_ref_with_vote_collection():
    data = {"value": [{"id": "u1"}, {"id": "u2", "vote": -10}]}
    col = IdentityRefWithVoteCollection.model_validate(data)
    assert col.count == 2
    assert col[1].vote == VoteEnum.rejected


# ---------------------------------------------------------------------------
# IdentityRefCreate
# ---------------------------------------------------------------------------


def test_identity_ref_create_minimal():
    ref = IdentityRefCreate(id="user-1")
    dump = ref.model_dump(exclude_none=True)
    assert dump == {"id": "user-1"}


def test_identity_ref_create_with_is_required():
    ref = IdentityRefCreate(id="user-1", isRequired=True)
    dump = ref.model_dump(exclude_none=True)
    assert dump["isRequired"] is True


def test_identity_ref_create_with_vote():
    ref = IdentityRefCreate(id="user-1", vote=10)
    assert ref.vote == VoteEnum.approved
    dump = ref.model_dump(exclude_none=True)
    assert "vote" in dump


# ---------------------------------------------------------------------------
# PullRequestClient
# ---------------------------------------------------------------------------


def test_pr_client_find_existing_thread_found(mock_session):
    thread_with_plan = {
        **PR_THREAD_SPEC,
        "properties": {"tfci.plan": {"$type": "System.String", "$value": "my-plan"}},
    }
    payload = {"value": [PR_THREAD_SPEC, thread_with_plan]}
    mock_session.get.return_value = ok_response(payload)
    client = PullRequestClient(mock_session)

    result = client.find_existing_thread(pr_id=42, plan="my-plan")

    assert result is not None
    assert result.properties["tfci.plan"].value == "my-plan"


def test_pr_client_find_existing_thread_not_found(mock_session):
    payload = {"value": [PR_THREAD_SPEC]}
    mock_session.get.return_value = ok_response(payload)
    client = PullRequestClient(mock_session)

    result = client.find_existing_thread(pr_id=42, plan="nonexistent-plan")

    assert result is None


def test_pr_client_find_existing_thread_skips_deleted(mock_session):
    deleted_thread = {
        **PR_THREAD_SPEC,
        "isDeleted": True,
        "properties": {"tfci.plan": {"$type": "System.String", "$value": "my-plan"}},
    }
    payload = {"value": [deleted_thread]}
    mock_session.get.return_value = ok_response(payload)
    client = PullRequestClient(mock_session)

    result = client.find_existing_thread(pr_id=1, plan="my-plan")

    assert result is None


def test_pr_client_delete_thread_comments(mock_session):
    del_resp = MagicMock()
    del_resp.status_code = 204
    mock_session.delete.return_value = del_resp

    thread = PullRequestThread.model_validate(
        {
            **PR_THREAD_SPEC,
            "comments": [PR_COMMENT_SPEC, {**PR_COMMENT_SPEC, "id": 2}],
        }
    )
    client = PullRequestClient(mock_session)
    client.delete_thread_comments(pr_id=7, thread=thread)

    assert mock_session.delete.call_count == 2


def test_pr_client_new_thread(mock_session):
    post_resp = MagicMock()
    post_resp.status_code = 200
    mock_session.post.return_value = post_resp
    client = PullRequestClient(mock_session)

    thread = PullRequestThreadCreate(comments=[PullRequestThreadCommentCreate(content="note")])
    client.new_thread(pr_id=5, thread=thread)

    mock_session.post.assert_called_once()
    url_arg = mock_session.post.call_args[0][0]
    assert url_arg == "/5/threads"


def test_pr_client_list_reviewers(mock_session):
    payload = {"value": [{"id": "u1"}, {"id": "u2"}]}
    mock_session.get.return_value = ok_response(payload)
    client = PullRequestClient(mock_session)

    result = client.list_reviewers(pr_id=3)

    assert isinstance(result, IdentityRefWithVoteCollection)
    assert result.count == 2
    mock_session.get.assert_called_once_with("/3/reviewers", params=None)


def test_pr_client_add_reviewers(mock_session):
    payload = {"value": [{"id": "u1", "vote": 0}]}
    post_resp = MagicMock()
    post_resp.status_code = 200
    post_resp.json.return_value = payload
    mock_session.post.return_value = post_resp
    client = PullRequestClient(mock_session)

    reviewers = [IdentityRefCreate(id="u1")]
    result = client.add_reviewers(pr_id=3, reviewers=reviewers)

    assert isinstance(result, IdentityRefWithVoteCollection)
    mock_session.post.assert_called_once()
    url_arg = mock_session.post.call_args[0][0]
    assert url_arg == "/3/reviewers"


def test_pr_client_remove_reviewer(mock_session):
    del_resp = MagicMock()
    del_resp.status_code = 204
    mock_session.delete.return_value = del_resp
    client = PullRequestClient(mock_session)

    client.remove_reviewer(pr_id=3, reviewer_id="user-abc")

    mock_session.delete.assert_called_once_with("/3/reviewers/user-abc", params=None)


def test_pr_client_require_identity_client_raises(mock_session):
    client = PullRequestClient(mock_session, identity_client=None)
    with pytest.raises(ValueError):
        client._require_identity_client()


def test_pr_client_require_identity_client_returns(mock_session):
    identity_client = MagicMock(spec=IdentityClient)
    client = PullRequestClient(mock_session, identity_client=identity_client)
    assert client._require_identity_client() is identity_client
