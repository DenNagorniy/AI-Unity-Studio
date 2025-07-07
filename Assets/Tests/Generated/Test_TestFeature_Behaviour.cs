using UnityEngine.TestTools;
using NUnit.Framework;
using UnityEngine;
using System.Collections;

namespace AIUnityStudio.Generated.Tests
{
    public class Test_TestFeature_Behaviour
    {
        [UnityTest]
        public IEnumerator TestFeatureExistsInScene()
        {
            var go = GameObject.FindObjectOfType<TestFeature>();
            Assert.IsNotNull(go, "TestFeature script is not found in the scene.");
            yield return null;
        }
    }
}
