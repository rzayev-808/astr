import json
from django.test import TestCase
from rest_framework.test import APIClient
from pricing.models import Pricing
from user.models import User
from space.models import Space
from squads.models import Squad
from cluster.models import Cluster
from task.models import Project, Task
from invite.models import Invite


class ApiSmokeTest(TestCase):
    def setUp(self):
        Pricing.objects.create(name="Free")
        self.owner = User.objects.create(email="owner@test.az", fullname="Owner")
        self.member = User.objects.create(email="member@test.az", fullname="Member")
        self.c = APIClient()
        self.c.force_authenticate(user=self.owner)
        self.space = Space.objects.filter(creater_user=self.owner).first()

    def test_space_crud_and_members(self):
        r = self.c.post("/space/api/", {"space_name": "Yeni Space"}, format="json")
        self.assertEqual(r.status_code, 201, r.content)
        new_id = r.json()["id"]

        r = self.c.get("/space/api/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.json()), 2)

        r = self.c.patch(f"/space/api/{new_id}/", {"company": "ABB"}, format="json")
        self.assertEqual(r.status_code, 200, r.content)
        self.assertEqual(r.json()["company"], "ABB")

        r = self.c.post(f"/space/api/{new_id}/members/", {"user": self.member.id}, format="json")
        self.assertEqual(r.status_code, 200, r.content)
        self.assertIn(self.member, Space.objects.get(pk=new_id).members.all())

        r = self.c.delete(f"/space/api/{new_id}/members/{self.member.id}/")
        self.assertEqual(r.status_code, 200, r.content)
        self.assertNotIn(self.member, Space.objects.get(pk=new_id).members.all())

        r = self.c.delete(f"/space/api/{new_id}/")
        self.assertEqual(r.status_code, 204, r.content)
        self.assertFalse(Space.objects.filter(pk=new_id).exists())

        # başqasının space-ini silmək olmaz
        other_space = Space.objects.filter(creater_user=self.member).first()
        r = self.c.delete(f"/space/api/{other_space.id}/")
        self.assertEqual(r.status_code, 404)

    def test_squad_crud(self):
        r = self.c.post("/squad/api/", {"name": "Alpha", "space": self.space.id,
                                        "squad_members": [self.member.id]}, format="json")
        self.assertEqual(r.status_code, 201, r.content)
        sq_id = r.json()["id"]

        r = self.c.get("/squad/api/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.json()), 1)

        r = self.c.get(f"/squad/api/{sq_id}/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["name"], "Alpha")

        r = self.c.patch(f"/squad/api/{sq_id}/", {"name": "Beta"}, format="json")
        self.assertEqual(r.status_code, 200, r.content)
        self.assertEqual(Squad.objects.get(pk=sq_id).name, "Beta")

        r = self.c.delete(f"/squad/api/{sq_id}/")
        self.assertEqual(r.status_code, 204)
        self.assertFalse(Squad.objects.filter(pk=sq_id).exists())

    def test_cluster_crud(self):
        r = self.c.post("/cluster/api/", {"name": "C1", "space": self.space.id}, format="json")
        self.assertEqual(r.status_code, 201, r.content)
        cl_id = r.json()["id"]

        r = self.c.get("/cluster/api/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.json()), 1)

        # retrieve artıq real retrieve-dir: tək obyekt, düzgün id
        r = self.c.get(f"/cluster/api/{cl_id}/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["id"], cl_id)

        r = self.c.patch(f"/cluster/api/{cl_id}/", {"name": "C2"}, format="json")
        self.assertEqual(r.status_code, 200, r.content)

        r = self.c.delete(f"/cluster/api/{cl_id}/")
        self.assertEqual(r.status_code, 204)

    def test_project_crud(self):
        r = self.c.post("/task/api/project/", {"name": "P1"}, format="json")
        self.assertEqual(r.status_code, 201, r.content)
        p_id = r.json()["id"]

        r = self.c.get("/task/api/project/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.json()), 1)

        r = self.c.get(f"/task/api/project/{p_id}/")
        self.assertEqual(r.status_code, 200)

        r = self.c.patch(f"/task/api/project/{p_id}/", {"name": "P2"}, format="json")
        self.assertEqual(r.status_code, 200, r.content)

        r = self.c.delete(f"/task/api/project/{p_id}/")
        self.assertEqual(r.status_code, 204)

    def test_task_create_not_shadowed(self):
        # api/<pk> əvvəllər api/create-i udurdu → POST 405 qayıdırdı
        squad = Squad.objects.create(name="S", space=self.space)
        project = Project.objects.create(name="P")
        r = self.c.post("/task/api/create/", {
            "name": "T1", "squad": squad.id, "project": project.id,
            "deadline": "2026-09-01T12:00:00Z", "description": "d",
            "story_point": "3", "status": "To Do",
        }, format="json")
        self.assertEqual(r.status_code, 201, r.content)
        self.assertEqual(Task.objects.count(), 1)

    def test_invite_flow(self):
        r = self.c.post("/invite/api/", {"email": "member@test.az", "role": "dev",
                                         "space": self.space.id}, format="json")
        self.assertEqual(r.status_code, 200, r.content)
        inv_id = r.json()["invite"]["id"]
        self.assertEqual(Invite.objects.get(pk=inv_id).invited_by, self.owner)

        r = self.c.get("/invite/api/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.json()), 1)

        r = self.c.get("/invite/api/?acceptance=false")
        self.assertEqual(len(r.json()), 1)
        r = self.c.get("/invite/api/?acceptance=true")
        self.assertEqual(len(r.json()), 0)

        # yad user qəbul edə bilməz
        stranger = User.objects.create(email="x@test.az", fullname="X")
        c2 = APIClient(); c2.force_authenticate(user=stranger)
        r = c2.post(f"/invite/api/{inv_id}/accept/")
        self.assertEqual(r.status_code, 403)

        # dəvət olunan qəbul edir → space üzvü olur
        c3 = APIClient(); c3.force_authenticate(user=self.member)
        r = c3.post(f"/invite/api/{inv_id}/accept/")
        self.assertEqual(r.status_code, 200, r.content)
        self.assertTrue(Invite.objects.get(pk=inv_id).acceptance)
        self.assertIn(self.member, self.space.members.all())

        # cancel (sil)
        r = self.c.delete(f"/invite/api/{inv_id}/")
        self.assertEqual(r.status_code, 204)
        self.assertFalse(Invite.objects.filter(pk=inv_id).exists())

    def test_swagger_contains_new_endpoints(self):
        r = self.client.get("/auth/api/swagger.json", follow=True)
        self.assertEqual(r.status_code, 200)
        paths = json.loads(r.content)["paths"]
        for p in ["/space/api/", "/space/api/{id}/", "/space/api/{id}/members/",
                  "/space/api/{id}/members/{user_id}/",
                  "/squad/api/", "/squad/api/{id}/",
                  "/cluster/api/", "/cluster/api/{id}/",
                  "/task/api/project/", "/task/api/project/{id}/",
                  "/invite/api/", "/invite/api/{id}/", "/invite/api/{id}/accept/"]:
            self.assertIn(p, paths, f"{p} swagger-də yoxdur")
        self.assertIn("post", paths["/space/api/"])
        self.assertIn("delete", paths["/space/api/{id}/"])
        self.assertIn("post", paths["/squad/api/"])
        self.assertIn("delete", paths["/squad/api/{id}/"])
        self.assertIn("post", paths["/cluster/api/"])
        self.assertIn("post", paths["/task/api/project/"])
        self.assertIn("get", paths["/invite/api/"])
        self.assertIn("delete", paths["/invite/api/{id}/"])
