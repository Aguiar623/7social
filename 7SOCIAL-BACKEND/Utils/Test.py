import unittest
from Utils.Analisis import analizar_emocion

class TestAnalisisEmocional(unittest.TestCase):

    def test_emocion_positiva(self):
        posts = [{"content": "Me siento muy feliz con los resultados"}]
        emocion, probas = analizar_emocion(posts)
        self.assertIn(emocion, ["others", "joy", "sadness", "anger", "surprise", "disgust", "fear"])
        self.assertAlmostEqual(sum(probas.values()), 1.0, places=2)
        print("1.Emoción dominante:", emocion)
        print("1.Probabilidades:", probas)

    def test_emocion_negativa(self):
        posts = [{"content": "Estoy cansado de todo, nada tiene sentido"}]
        emocion, probas = analizar_emocion(posts)
        self.assertIn(emocion, ["others", "joy", "sadness", "anger", "surprise", "disgust", "fear"])
        self.assertAlmostEqual(sum(probas.values()), 1.0, places=2)
        print("2.Emoción dominante:", emocion)
        print("2.Probabilidades:", probas)

    def test_entrada_vacia(self):
        posts = [{"content": ""}]
        emocion, probas = analizar_emocion(posts)
        self.assertIsInstance(emocion, str)
        self.assertIsInstance(probas, dict)
        print("3.Emoción dominante:", emocion)
        print("3.Probabilidades:", probas)

    def test_entrada_multiple(self):
        posts = [
            {"content": "Estoy feliz por terminar el proyecto."},
            {"content": "Aunque también me siento algo estresado."}
        ]
        emocion, probas  = analizar_emocion(posts)
        self.assertIn(emocion, ["others", "joy", "sadness", "anger", "surprise", "disgust", "fear"])
        self.assertAlmostEqual(sum(probas.values()), 1.0, places=2)
        print("4.Emoción dominante:", emocion)
        print("4.Probabilidades:", probas)

    def test_entrada_simbolos(self):
        posts = [{"content":"###@@@"}]
        emocion, probas = analizar_emocion(posts)
        self.assertIn(emocion, ["others", "joy", "sadness", "anger", "surprise", "disgust", "fear"])
        self.assertAlmostEqual(sum(probas.values()), 1.0, places=2)
        print("5.Emocion Dominante:", emocion)
        print("5.Probabilidades:", probas)

    def test_entrada_simbolos_sorpresa(self):
        posts = [{"content":"???"}]
        emocion, probas = analizar_emocion(posts)
        self.assertIn(emocion, ["others", "joy", "sadness", "anger", "surprise", "disgust", "fear"])
        self.assertAlmostEqual(sum(probas.values()), 1.0, places=2)
        print("6.Emocion Dominante:", emocion)
        print("6.Probabilidades:", probas)

    def test_entrada_sin_sentido(self):
        posts = [{"content":"ewtgergrehbtehsdferg"}]
        emocion, probas = analizar_emocion(posts)
        self.assertIn(emocion, ["others","joy","sadness","anger","surprise","disgust","fear"])
        self.assertAlmostEqual(sum(probas.values()),1.0, places=2)
        print("7.Emocion Dominante:", emocion)
        print("7.Probabilidades:", probas)

if __name__ == "__main__":
    unittest.main()
