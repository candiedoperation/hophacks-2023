from roboflow import Roboflow

rf = Roboflow(api_key="tF51WFIm1hXPxzxz8KFZ")
project = rf.workspace().project("cvusa_aerials_segmentation")
model = project.version(3).model

print(model.predict("2.jpeg").json())
