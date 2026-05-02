import pytest
import farmsure.db as db


class TestCreateClaim:
    def test_returns_claim_number_string(self, make_claim):
        number = make_claim()
        assert isinstance(number, str)

    def test_claim_number_format(self, make_claim):
        number = make_claim()
        parts = number.split("-")
        assert parts[0] == "CLM"
        assert parts[1].isdigit() and len(parts[1]) == 4  # year
        assert parts[2].isdigit() and len(parts[2]) == 5  # zero-padded sequence

    def test_sequential_numbers_increment(self, make_claim, make_user):
        uid = make_user()
        n1 = make_claim(user_id=uid)
        n2 = make_claim(user_id=uid)
        seq1 = int(n1.split("-")[2])
        seq2 = int(n2.split("-")[2])
        assert seq2 == seq1 + 1

    def test_default_status_is_pending(self, make_claim, make_user):
        uid = make_user()
        number = make_claim(user_id=uid)
        claims = db.get_user_claims(uid)
        assert claims[0]["status"] == "Pending"

    def test_optional_acres_can_be_none(self, make_claim, make_user):
        uid = make_user()
        make_claim(user_id=uid, affected_acres=None)
        claims = db.get_user_claims(uid)
        assert claims[0]["affected_acres"] is None


class TestGetUserClaims:
    def test_empty_for_new_user(self, make_user):
        uid = make_user()
        assert db.get_user_claims(uid) == []

    def test_returns_own_claims_only(self, make_claim, make_user):
        uid1 = make_user(email="u1@farm.com")
        uid2 = make_user(email="u2@farm.com")
        make_claim(user_id=uid1)
        make_claim(user_id=uid1)
        make_claim(user_id=uid2)
        assert len(db.get_user_claims(uid1)) == 2
        assert len(db.get_user_claims(uid2)) == 1

    def test_ordered_newest_first(self, make_claim, make_user):
        uid = make_user()
        n1 = make_claim(user_id=uid)
        n2 = make_claim(user_id=uid)
        claims = db.get_user_claims(uid)
        assert claims[0]["claim_number"] == n2
        assert claims[1]["claim_number"] == n1

    def test_claim_fields_present(self, make_claim, make_user):
        uid = make_user()
        make_claim(user_id=uid, crop_type="Cotton", estimated_loss=5000.0)
        claim = db.get_user_claims(uid)[0]
        assert claim["crop_type"] == "Cotton"
        assert claim["estimated_loss"] == 5000.0
        assert "claim_number" in claim
        assert "status" in claim


class TestGetClaimStats:
    def test_all_zeros_for_new_user(self, make_user):
        uid = make_user()
        stats = db.get_claim_stats(uid)
        assert stats["total"] == 0
        assert stats["total_claimed"] == 0

    def test_counts_by_status(self, make_claim, make_user):
        from farmsure.db.connection import get_connection, _cur

        uid = make_user()
        n1 = make_claim(user_id=uid, estimated_loss=1000.0)
        n2 = make_claim(user_id=uid, estimated_loss=2000.0)
        n3 = make_claim(user_id=uid, estimated_loss=3000.0)

        conn = get_connection()
        c = _cur(conn)
        c.execute("UPDATE claims SET status='Approved'  WHERE claim_number=%s", (n1,))
        c.execute("UPDATE claims SET status='Rejected'  WHERE claim_number=%s", (n2,))
        conn.commit()
        conn.close()

        stats = db.get_claim_stats(uid)
        assert stats["total"]    == 3
        assert stats["approved"] == 1
        assert stats["rejected"] == 1
        assert stats["pending"]  == 1

    def test_total_claimed_sums_losses(self, make_claim, make_user):
        uid = make_user()
        make_claim(user_id=uid, estimated_loss=1000.0)
        make_claim(user_id=uid, estimated_loss=2500.0)
        stats = db.get_claim_stats(uid)
        assert stats["total_claimed"] == pytest.approx(3500.0)

    def test_ignores_other_users_claims(self, make_claim, make_user):
        uid1 = make_user(email="s1@farm.com")
        uid2 = make_user(email="s2@farm.com")
        make_claim(user_id=uid1)
        make_claim(user_id=uid1)
        make_claim(user_id=uid2)
        assert db.get_claim_stats(uid1)["total"] == 2
        assert db.get_claim_stats(uid2)["total"] == 1


class TestGetAllClaims:
    def test_returns_all_when_no_filter(self, make_claim, make_user):
        uid1 = make_user(email="a1@farm.com")
        uid2 = make_user(email="a2@farm.com")
        make_claim(user_id=uid1)
        make_claim(user_id=uid2)
        assert len(db.get_all_claims()) == 2

    def test_filter_by_status(self, make_claim, make_user):
        from farmsure.db.connection import get_connection, _cur

        uid = make_user()
        n1 = make_claim(user_id=uid)
        n2 = make_claim(user_id=uid)

        conn = get_connection()
        c = _cur(conn)
        c.execute("UPDATE claims SET status='Approved' WHERE claim_number=%s", (n1,))
        conn.commit()
        conn.close()

        approved = db.get_all_claims("Approved")
        pending  = db.get_all_claims("Pending")
        assert len(approved) == 1
        assert len(pending)  == 1

    def test_all_filter_returns_everything(self, make_claim, make_user):
        uid = make_user()
        make_claim(user_id=uid)
        make_claim(user_id=uid)
        assert len(db.get_all_claims("All")) == 2

    def test_includes_joined_farmer_fields(self, make_claim, make_user):
        uid = make_user(full_name="Farmer Joe", email="joe@farm.com")
        make_claim(user_id=uid)
        claim = db.get_all_claims()[0]
        assert claim["full_name"] == "Farmer Joe"
        assert claim["user_email"] == "joe@farm.com"

    def test_empty_db_returns_empty_list(self):
        assert db.get_all_claims() == []


class TestUpdateClaimStatus:
    def test_status_changes(self, make_claim, make_user):
        uid = make_user()
        number = make_claim(user_id=uid)
        claims = db.get_user_claims(uid)
        claim_id = claims[0]["id"]

        db.update_claim_status(claim_id, "Approved")
        updated = db.get_user_claims(uid)[0]
        assert updated["status"] == "Approved"

    def test_multiple_status_transitions(self, make_claim, make_user):
        uid = make_user()
        make_claim(user_id=uid)
        claim_id = db.get_user_claims(uid)[0]["id"]

        for status in ["Under Review", "Approved", "Rejected", "Under Review"]:
            db.update_claim_status(claim_id, status)
            assert db.get_user_claims(uid)[0]["status"] == status


class TestGetAllClaimStats:
    def test_empty_db(self):
        stats = db.get_all_claim_stats()
        assert stats["total"] == 0
        assert float(stats["total_claimed"]) == 0.0

    def test_counts_across_all_users(self, make_claim, make_user):
        uid1 = make_user(email="as1@farm.com")
        uid2 = make_user(email="as2@farm.com")
        make_claim(user_id=uid1, estimated_loss=5000.0)
        make_claim(user_id=uid2, estimated_loss=3000.0)
        stats = db.get_all_claim_stats()
        assert stats["total"] == 2
        assert float(stats["total_claimed"]) == pytest.approx(8000.0)
