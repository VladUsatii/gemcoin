# crawlerdata.py
# Author: Vlad Usatii @ gemcoin
"""
GEMCOIN CRAWLERS

Gemcoin is armed with crawlers that have special privileges. These crawlers are read-only and simply exist to query the blockchain for other apps. A special reconstruction will happen in the near future that will create decentralized crawlers. Currently, our architecture supports a centralized list of actions that result in chain querying for L1.

"""

crawler_pubkeys = [
	'92de3c33b92344e04f011c00d7dbbe9e24c9e00f94e07fd36533d45e0ad147f2bd9510f088226a2714b900f4a02a9c5aa667b07fb9f23632712fefdb1bd24789',
	'1648b9f8303a04861b00d19dd17fc3f6985df954eb33a01ab1d1389c0e8c52980826ca3590b82cb1e88cd44f97bc8a8a81d99823f2291a58d9346b26ed92f003',
	'6c81355c1759a0cbf361d94b1b7012ddc13544f0d398617f1033a7d44b9c767aa381778eb06a9fa4ed55c83f403675377b147b296164a84f1cf32be76ec2708a',
	'07db33a025c83d7f68879331ac77bfe7f574f95674081eefe4bdd7f49011ee20c4b889ef616fa49d453ad02721b498f0c6836e9c4cbacfcd9cbf055df02c55a6',
	'eeba8e341634d1680a687e990595d1d41f41978996558eda478a144528d9297f65e888009df647a1045e795dc114c6524f8ae4ba177c220dda01924ea0558d8b',
	'e4034b872617bb27b187f44e20cded91c1b27c72ac4ce9c2ef8616d9d049fb7806d3964dc95edde8752f202dc6a708c10a89dd0b40bbca8f39c3a8d64527442c',
	'8f24f926e026575c0cb864d9bbf238bcc9b10d1b2d28fa0d0aab3369017c988b0a329c2bfe614b8b8d9f569bca06de8dd5110fe2ce3f0900399b8ff0722f8e34',
	'12dc20e944992f492b3b623514721546b35ec1d32b554031ef83f8ea7e8eb4ba917a649052e0ed38f7388fe2ac8cc37541441af1da5b22bf77048d6d2a510fb9',
	'f4f841aa530a25eb00f05285e0dfa57eaecfa21ba741a54fb79869e4d26dec0ae940b6ecea7af695cd50461e96fc7356b906142a69765ca5d80e4fddd321a204',
	'dff02f84668a5bd9bf8f9736aa4f9a280c025ddc7c292b6f3c1189eb8084e8de1ae7a7ef879f95b2d748468562e8ef387c3020b7c47fc3ffb1487c3cdf8badee',
	'7abad8ef9638a71e5af4feb6f48eb6f8532e85b604bbdaf4f97c92d1a9d2c797bbad1a8e06df797032059459bdf1b5ad81d1bf2ffff0bce8d34783c47fac86c2',
	'c087fc41f56bb65c402e418873d3a9f32d3fc54bc7ef68b092e2c3976052c86db948ec992cba04d7adfedfcb82fcffcefaaf730d1a9f089bfb495d56de3af213',
	'abc60cb8806c77bd9949895c7d49f632850847ee8deca4cb13d35f07da26a1f882b5e05114104a754e0b0895ba4435a25e5852cc43d08f52b648e11c6f5d9111',
	'7fadbbcb07abb955ce3e1c7051f705c52108b9dff9069fb1c20fbd82cf3bd5d56c72f632ef5f5c24da8f3a5f0b62168e5e8ff2e1877272af6bfe9cdfb3184ec2',
	'a47eac0b1216649cf327623db5984467e0e186ac60fdc1e8d69bc9fb3c5e46a51e29362d0e5f2a5ec33d109215bc410f5da2f056a3e48e67a4084acc4c144644',
	'db9d709b5ce55b84a821d61cf7e80bd7db8f5889cb226193b3740a314bf290a92b24e4fb33ce3cb7e05f0510a08d8bf94aaa557423b76f470a10888fcc476288',
	'08c86699539081378d79937d570f1a5b24d0b124dd37755bc02d7f761414a6152fdbc4287bb78ab97436a4a8bd359498489990eb73215e2d1dfe2e7e33baa2df',
	'4bff94612f5ec26d7310a024ca8fd78c801e8880c5a07365930bd0edcdde6ebd56b2bd74f7838be91b88159a0482a14aa0d187750a2286a1b8c1d0fd8415d197',
	'82ee0aca12fac3bffe911fdde16b43f01d9c5cd9803341e388175fcd3cd4534c39cafa593cd075809e4a003225baec8028eeef165a01fb03f6f28f8f642ceaa5',
	'e3c3d2a93a39a6c6d5a01cae0432965af593de2027c0a6d801ee32cafd5c1468af9e4e806c3a79fa725f21dc017e391ec2ad4690b1d65fa19ba41480d6e529fa',
	'f63669841b34113e7c36fa15ab71252dff08bd3414fff8933517714d7f635bc28b1ed4fdf538ed2ba2cef72c1e59d79351f26fd4a34f4f8db6de9aa052435a31',
	'4dabe50fd3428eb79589c9fe0672e6a38d2b8c1a7d68b566dc0dfb649cf33b2a5d16bd5219d6cae65e63488c213c1f1c0eef3a7e7907d6ac654b6c8f70ca28e2',
	'ed8a67d920ff2711f3b4d5a21c057396f6d7f849fe84b61b889e8ae7344aa43bca5ab28c03a6714033489e1a3ca57f6d7b99d23c22a19e7592720a7af589f98e',
	'a6fa8bb173363adc8a431a5213aee5d214d68b17fdfb38bf550e1e19c5a548faef84d6336e7e6e1eb1ccf0f51e9807744e03f090ba5c16c1c5c5aa3848703295',
	'12c98ab4963814ed151e4b0fc8fd64abb9c236113bb01dee693d2557ebd66acd4b101c7f194624bd2cefc8f93bae2485691ffd551a26e25c39e439f656d8387b',
	'abee85370fa05e337f0e236108f1c4c8ec9f5095c470157dc223d4a28d6e5bf673a09c9d6df43ee4e98241cf2a365eb44fbb956b36138a56e42c6091b6f91ada',
	'b2f4634ae1b96d144af846ad46fc78c6e1a091c329a8a0fc4fbf53a4292f150b77b2dcaa88d073d1d01522e75b144040b38870c42ee1b1312a7e8f64ea264e81',
	'e23efe1710a5931fea55a66209e1fa275d4bebdd769da0c3b5bfa8b78d7b9de48e396e9bfe8aa20d72185b84e3746decd6878ce0054d95c7fe0fed413b2216dd',
	'75b5c8fb9593295691b8601768e8cc43de0edcd26b7ed89a11f533fb4a57a8d945f0b885f114eff3b70f11856ce143756502fe58f4c2615706c7caa58dd5f1f9',
	'a737bff27d7d19be044852eba419e1d51359d11bdc3d7546d8f075b497ed79d96d9aa9131a1331d071960911aeea7c953b837e10617c1c25e5521bbdb7f5345f',
	'c4c0d32afaae8843555a382c16b9298f034ce5d4055736fd759d881a4b0aaab841dcebb47f9beef9f4e5fb912dfd495ac00982b6cab7a2bdc6d4c0296ae68db0',
	'acde5bdcdf3673456c6fe190aa4d1de3f76955a75be54f18d1aee772c396a685b21c45a895707931de4a657e927b3abd179ebfb722b56f77ac5c75ccd3ea03b2'
]