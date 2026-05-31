# -*- coding: utf-8 -*-
import random
from locust import HttpUser, task, between, TaskSet

class EstudianteTaskSet(TaskSet):
    """
    Simulación probabilística de interacciones reales de Alumnos de la Academia:
    - 30% navega al portal personal.
    - 40% explora los cursos LMS e e-Learning.
    - 10% completa su onboarding obligatorio.
    - 20% agrega cursos de TI a su carrito.
    """

    @task(30)
    def ver_mi_portal(self):
        self.client.get("/my", headers={"Accept": "text/html"})

    @task(40)
    def explorar_cursos_lms(self):
        self.client.get("/slides", headers={"Accept": "text/html"})
        # Simula la lectura de un curso específico de los 10 configurados
        curso_id = random.randint(1, 10)
        self.client.get(f"/slides/slide-channel-{curso_id}", headers={"Accept": "text/html"})

    @task(10)
    def enviar_onboarding_preferencias(self):
        payload = {
            "interest_ids": [1, 2],
            "birthday": "1995-05-29",
            "experience_level": "intermediate",
            "terms_accepted": "on",
            "privacy_accepted": "on"
        }
        self.client.post("/my/email-preferences/submit", data=payload)

    @task(20)
    def agregar_curso_a_carrito(self):
        # Envía la petición síncrona JSON que intercepta das_lms
        payload = {
            "product_id": random.choice([1, 5, 8]), # ASI, IA, Sistemas
            "add_qty": 1
        }
        self.client.post("/shop/cart/update_json", json=payload)

class EstudianteSimulado(HttpUser):
    tasks = [EstudianteTaskSet]
    wait_time = between(1, 5) # Simula retraso humano de lectura entre clics (1-5 segundos)