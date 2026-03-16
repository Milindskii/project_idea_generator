export const MOCK_RESULTS = {
  analysis: "Based on your interest in AI and your beginner skill level, your idea of helping farmers detect crop disease is highly feasible. It maps well to computer vision and machine learning. Given your 3-month timeline, a focused MVP is achievable. We recommend starting with a pretrained model and a simple web interface.",
  projects: [
    {
      id: 1,
      title: "AgriVision Mobile",
      description: "A lightweight mobile app that uses a smartphone camera to identify common leaf diseases in tomato plants using TensorFlow Lite.",
      techStack: ["React Native", "TensorFlow Lite", "Python"],
      difficulty: "Intermediate",
      matchScore: 98
    },
    {
      id: 2,
      title: "CropHealth Dashboard",
      description: "A web-based analytics platform for farmers to upload crop photos and track disease outbreaks geographically over time.",
      techStack: ["React", "Flask", "PostgreSQL", "OpenCV"],
      difficulty: "Beginner",
      matchScore: 92
    },
    {
      id: 3,
      title: "Smart Irrigation AI",
      description: "An IoT-integrated system that predicts water needs based on soil moisture sensors and visual plant health analysis.",
      techStack: ["Raspberry Pi", "Python", "AWS IoT", "Scikit-learn"],
      difficulty: "Advanced",
      matchScore: 85
    }
  ]
};
