ENTITY_TYPES = {
    "Person": "Từ hoặc cụm từ chỉ người, bao gồm cả đại từ nhân xưng.\n\nLƯU Ý: Mọi tham chiếu đến cá nhân hoặc nhóm người — tên riêng, đại từ (ông, bà, anh, chị, họ, ta, nó, mình...) và cụm danh từ chỉ người (người, dân, nạn nhân, bị can, cảnh sát, tài xế, hành khách, công nhân, cầu thủ, bác sĩ, giáo viên...) khi chúng chỉ những người tham gia thực sự trong câu.",
    "Organization": "Danh từ riêng hoặc cụm từ chỉ tổ chức, cơ quan, công ty, chính phủ, nhóm xã hội, tổ chức chính trị hoặc quân sự.\n\nLƯU Ý: Mọi nhóm, tổ chức hoặc cơ quan chính thức hay phi chính thức — cơ quan nhà nước, công ty, tòa án, ngân hàng, bệnh viện, đảng phái, đơn vị quân đội, trường học. Các từ viết tắt thông dụng (toà, công ty, ngân hàng, đại sứ quán, uỷ ban, cơ quan, bộ, ban) đều là thực thể Organization hợp lệ.",
    "Geopolitical-Entity": "Khu vực địa lý có liên quan đến một chính phủ, chẳng hạn như quốc gia, thành phố, tỉnh, bang hoặc khu vực.\n\nVí dụ:\n- Quốc gia: Việt Nam, Hoa Kỳ, Pháp\n- Thành phố: Hà Nội, Thành phố Hồ Chí Minh, New York\n- Bang: California, Texas, New York\n- Khu vực: Châu Á, Châu Âu, Bắc Mỹ",
    "Location": "Địa điểm hoặc khu vực địa lý không liên quan đến chính phủ.\n\nBao gồm: tên địa điểm, vùng, quận, huyện, làng, xã, đường phố, địa chỉ cụ thể, các địa điểm tự nhiên (núi, sông, hồ, biển, sa mạc).\n\nVí dụ:\n- Địa điểm công cộng: Quảng trường Ba Đình, Công viên Thống Nhất, Bệnh viện Bạch Mai, Rạp hát Lớn\n- Địa điểm tự nhiên: Núi Tản Viên, Sông Hồng, Vịnh Hạ Long, Rừng Cát Tiên",
    "Facility": "Cơ sở hạ tầng do con người xây dựng — nhà ở, công trình, công trình công cộng.\n\nBao gồm: tòa nhà, công trình kiến trúc, công trình công cộng, khu vực xây dựng, địa điểm thể thao, cơ sở sản xuất.\n\nVí dụ:\n- \tTòa nhà: Nhà hát Thành phố, Bảo tàng Lịch sử Quốc gia, Tòa thị chính, Tòa án Nhân dân Hà Nội, Khách sạn Sofitel Metropole\n- \tCông trình: Cầu Long Biên, Tháp Eiffel, Đường cao tốc Nội Bài–Lào Cai\n- \tCơ sở thể thao: Sân vận động Hàng Đẫy, Nhà thi đấu Phú Thọ\n- \tKhu vực xây dựng: Công trường Formosa, Xưởng đóng tàu Bạch Đằng",
    "Weapon": "Bao gồm súng, đạn dược, dao, vũ khí tự chế.\n\nVí dụ:\n- Súng cá nhân: súng lục, súng ngắn, súng trường, súng ngắn ổ quay, súng bắn đinh, súng bắn hơi cay, súng bắn đạn cao su, súng săn\n- Vũ khí tự động: súng máy, súng carbine\n- Vũ khí hạng nặng: súng cối, súng cối tự hành, pháo phòng không, tên lửa, rocket, hệ thống tên lửa vác vai (MANPADS), súng phun lửa, súng phóng lựu\n- Vũ khí cận chiến: dao, kiếm, dao găm, mã tấu, gậy, dùi cui, dao rựa\n- Vũ khí tự chế: bom xăng, bom tự chế, thiết bị nổ ngẫu hứng (IED), mìn tự chế, lựu đạn tự chế\n- Đạn dược: đạn, viên đạn, đầu đạn, lựu đạn, bom, mìn, rocket, tên lửa\n\nLƯU Ý: \n- Xe quân sự khi được sử dụng như vũ khí tấn công hoặc phương tiện chiến đấu phải được phân loại là Weapon. Ví dụ: \"xe tăng nã đạn\" → Weapon:Xe tăng; \"xe tăng bị bắn hạ\" → Weapon:Xe tăng; \"trực thăng tấn công Apache\" → Weapon:Xe tăng.\n- Nếu danh từ chỉ vũ khí (súng, dao, bom, lựu đạn, vũ khí...) xuất hiện BẤT KỲ ĐÂU trong câu — kể cả khi nằm trong cụm động từ (nổ súng, cầm dao, ném bom, dùng súng bắn) — hãy trích xuất danh từ vũ khí đó. KHÔNG bỏ sót vũ khí ẩn trong cụm từ.",
    "Vehicle": "Phương tiện di chuyển — ô tô, máy bay, tàu thủy, xe lửa, xe máy và các phương tiện vận chuyển khác.\n\nVí dụ:\n- Đường bộ: xe ô tô, xe máy, xe tải, xe buýt, xe khách, xe taxi, xe cứu hỏa, xe cứu thương, xe cảnh sát, xe tăng, xe bọc thép, xe ben, xe đầu kéo\n- Hàng không: máy bay, trực thăng, máy bay phản lực, máy bay chở hàng, máy bay chiến đấu, tàu bay không người lái (drone), khinh khí cầu\n- Đường sắt: tàu hỏa, tàu điện, tàu điện ngầm (metro)\n- Đường thủy: tàu thủy, tàu ngầm, tàu chở hàng, tàu chở khách, ca nô, thuyền, xuồng, phà\n- Phương tiện đặc biệt: xe nâng, máy xúc, cần cẩu, xe lu\n\nLƯU Ý: Đối với xe quân sự, chỉ trích xuất khi câu mô tả hoạt động vận chuyển hoặc sử dụng xe như một phương tiện. Không trích xuất xe quân sự khi chúng được sử dụng như vũ khí tấn công (ví dụ: \"xe tăng nã đạn\" → Vehicle:Xe tăng; \"xe tăng bị bắn hạ\" → Weapon:Xe tăng).",
    "Time": "Mốc thời gian, ngày tháng, giờ giấc, khoảng thời gian, tần suất hoặc biểu thức thời gian tương đối.\n\nVí dụ:\n- Ngày 26/11, \n- Chiều 1/5, \n- ngày mai, \n- hôm qua, \n- 14h\n- năm 2026\n- 3 tháng\n- hàng tháng\n\nLƯU Ý: Trích xuất toàn bộ cụm từ chỉ thời gian không ngoại lệ, bao gồm cả các từ chỉ buổi trong ngày (chiều, sáng, tối).",
    "Money": "Số tiền hoặc giá trị tiền tệ, bao gồm tiền tệ quốc gia và quốc tế, mệnh giá, giá trị tài sản.\n\nBao gồm: giá trị tiền tệ bằng tiền quốc gia (VND) hoặc nước ngoài (USD, EUR, JPY, GBP...), bao gồm cả tiền mặt, chuyển khoản, thẻ, séc, phiếu mua hàng, hạn mức tín dụng, khoản nợ; và các biểu thức giá trị, tài sản được chuyển đổi sang tiền.\n\nVí dụ:\n- 500 triệu đồng, 1 tỷ đồng, 2,5 triệu USD\n- 50.000 VNĐ, 100.000 đồng\n- Khoản nợ 200 triệu, hạn mức tín dụng 5 tỷ\n- Giá trị tài sản 10 triệu đô la\n- Chi phí 10 tỷ đồng\n- Tiền bồi thường 500 triệu\n- Khoản thế chấp 2 tỷ\n- Hỗ trợ 300 triệu đồng\n- Khoản tài trợ 1 triệu USD\n- Tiền phạt 10 triệu đồng\n- Chi phí 500 triệu VNĐ\n- Giá trị cổ phiếu 1 tỷ USD\n- Mua 100 triệu cổ phiếu\n- Tài trợ 500 triệu cho dự án\n\nLƯU Ý: Các mặt hàng có giá trị cao (như vàng miếng, trang sức vàng, ngoại tệ) được đem đi giao dịch mua bán hoặc chuyển nhượng, thể hiện giá trị tiền tệ trong ngữ cảnh đó thì phải được phân loại là Money.",
    "Number": "Bao gồm số lượng chung, chỉ số, điểm số, tỷ lệ, đơn vị đếm, và các con số không thuộc các loại trên.\n\nVí dụ:\n- Số lượng: 100 người, 50kg, 2 mét, 10 chiếc\n- Điểm số, xếp hạng: top 10, hạng 5, điểm 10, top 1%\n- Tỷ lệ phần trăm: 5%, 10%, 50%\n- Đơn vị đếm: 100kg, 2 mét, 100 đơn vị\n- Số đếm chung: 123, 456789, 1000, số 1, số 2\n\nLƯU Ý: Trích xuất cả số ghi bằng chữ hoặc bằng số kèm theo đơn vị đo lường (tấn, tạ, mét...).",
    "Sentence": "Hình phạt pháp lý, mức án cụ thể do tòa án chính thức tuyên phạt đối với bị cáo.\n\nVí dụ:\n- Tuyên phạt 10 năm tù giam\n- Phạt 12 năm tù\n- Phạt 5 năm tù treo\n- Án tử hình\n- Phạt tiền 10 triệu đồng\n\nLƯU Ý: Chỉ trích xuất khi đó là một mức phạt/hình phạt pháp lý được đưa ra từ phán quyết của tòa án hoặc luật pháp.",
    "Crime": "Bao gồm các hành vi vi phạm pháp luật, tội danh, cáo buộc hoặc hành vi bất hợp pháp cụ thể\n\nVí dụ:\n- Giết người, giết người cướp của, giết người hàng loạt\n- Cướp tài sản, cướp tiệm vàng, cướp ngân hàng\n- Trộm cắp, trộm xe, trộm cắp tài sản\n- Lừa đảo, lừa đảo chiếm đoạt tài sản, lừa đảo qua mạng\n- Buôn bán, buôn bán vũ khí, buôn bán ma túy, buôn bán người, buôn bán động vật hoang dã\n- Vận chuyển, tàng trữ, tàng trữ vũ khí, tàng trữ ma túy\n- Đánh bạc, đánh bạc trực tuyến\n- Mua bán dâm, mại dâm\n- Rửa tiền, rửa tiền qua mạng\n- Xâm hại tình dục, hiếp dâm\n- Bạo hành, bạo hành gia đình, bạo hành trẻ em\n- Khủng bố, tài trợ khủng bố\n- Gian lận, gian lận thương mại, gian lận thuế, gian lận bảo hiểm\n- Xả thải, xả thải trái phép, xả thải hóa chất, xả thải vào sông\n- Phá hoại, phá hoại tài sản, phá hoại môi trường\n- Đốt phá, đốt rừng\n- Tàng trữ trái phép, tàng trữ vũ khí trái phép\n- Mua bán trái phép, mua bán ma túy trái phép, mua bán người trái phép",
    "Job": "Chức danh nghề nghiệp, vị trí công tác, nghề nghiệp hoặc vai trò chính thức của một cá nhân trong xã hội hoặc tổ chức.\n\nVí dụ:\n- Tổng thống\n- Thủ tướng\n- Bộ trưởng\n- Giám đốc\n- Cảnh sát trưởng\n- Tài xế\n- Bác sĩ\n- Nông dân\n\nLƯU Ý: Tránh bao gồm cả tên người đi kèm với chức danh nghề nghiệp khi không cần thiết, nếu tên người và chức danh nghề nghiệp được nhắc đến ở 2 span khác nhau thì có thể tách biệt."
}


EVENT_TYPES = {
    "Life:Be-Born": "Một người được sinh ra.\n- Ví dụ: sinh ra, chào đời, lọt lòng, hạ sinh.\n- Lưu ý: Trích xuất cả các từ ngữ văn chương hoặc trang trọng biểu thị việc một cá nhân bắt đầu cuộc sống.",
    "Life:Marry": "Hai người kết hôn hợp pháp hoặc tổ chức đám cưới.\n- Ví dụ: kết hôn, đám cưới, lấy vợ, lấy chồng, lập gia đình, thành hôn, vu quy.",
    "Life:Divorce": "Hai người ly hôn hoặc chấm dứt mối quan hệ hôn nhân hợp pháp.\n- Ví dụ: ly hôn, ly dị, đường ai nấy đi, huỷ hôn.",
    "Life:Injure": "Một người bị thương tích vật lý do tai nạn, thiên tai hoặc hành vi bạo lực của người khác.\n- Ví dụ: bị thương, gãy tay, trầy xước, chấn thương, nhập viện cấp cứu, trúng đạn (khi chỉ bị thương).\n- Lưu ý: Hành động gây thương tích có thể đi kèm với sự kiện tấn công, hãy trích xuất cả hai nếu có trigger riêng biệt.",
    "Life:Die": "Một người tử vong hoặc thiệt mạng do một sự kiện, bệnh tật hoặc hành động cụ thể.\n- Ví dụ: tử vong, thiệt mạng, qua đời, hy sinh, tử nạn, bị giết, mất, tử hình (khi nhấn mạnh việc chết).",
    "Movement:Transport": "Sự di chuyển của người, vũ khí, phương tiện hoặc hàng hóa từ nơi này sang nơi khác.\n- Ví dụ: vận chuyển, chở, áp giải, di chuyển, bay đến, cập cảng, điều động, chuyển đến, đi, đến.\n- Lưu ý: Bao gồm cả hành vi đi lại bình thường hoặc việc dịch chuyển mang tính chiến thuật/quân sự.",
    "Transaction:Transfer-Ownership": "Mua, bán, tặng hoặc chuyển nhượng quyền sở hữu hợp pháp của một tài sản, tổ chức hoặc đồ vật.\n- Ví dụ: bán, mua, chuyển nhượng, sang nhượng, đấu giá thành công, tậu, bàn giao (tài sản).",
    "Transaction:Transfer-Money": "Cho, nhận, chuyển, vay, quyên góp, tài trợ, trả tiền hoặc phạt tiền giữa các bên.\n- Ví dụ: chuyển khoản, thanh toán, giải ngân, cho vay, vay mượn, quyên góp, ủng hộ, hối lộ, nộp phạt.\n- Lưu ý: Bất kỳ hành động nào khiến dòng tiền/tài chính dịch chuyển từ chủ thể này sang chủ thể khác.",
    "Business:Start-Organization": "Thành lập, khai trương hoặc khởi đầu một tổ chức, công ty, cơ quan hoặc thực thể mới.\n- Ví dụ: thành lập, khai trương, thành lập công ty, mở cửa hàng, thành lập ban, lập hội.",
    "Business:Merge-Organization": "Hai hoặc nhiều tổ chức, doanh nghiệp sáp nhập, kết hợp lại thành một thực thể duy nhất.\n- Ví dụ: sáp nhập, hợp nhất, mua lại và sáp nhập (M&A), thôn tính.",
    "Business:Declare-Bankruptcy": "Một tổ chức hoặc cá nhân làm thủ tục hoặc chính thức tuyên bố phá sản hợp pháp.\n- Ví dụ: phá sản, tuyên bố phá sản, vỡ nợ, làm đơn phá sản.",
    "Business:End-Organization": "Một tổ chức, trường học, cơ quan hoặc doanh nghiệp bị giải thể, đóng cửa, ngừng hoạt động hoặc chấm dứt hoàn toàn.\n- Ví dụ: giải thể, đóng cửa, phá dỡ, đóng cửa vĩnh viễn, dừng hoạt động.",
    "Conflict:Attack": "Một hành vi bạo lực vật lý, tấn công vũ trang hoặc hành hung nhằm gây hại, tổn thương hoặc phá hoại chủ thể khác.\n- Ví dụ: tấn công, nổ súng, đâm, chém, đánh đập, oanh tạc, ném bom, kích nổ, ám sát, xả súng.\n- Lưu ý: Nếu một cụm từ chứa cả hành động tấn công và vũ khí (ví dụ: \"dùng dao đâm\" -> trích xuất \"đâm\").",
    "Conflict:Demonstrate": "Một cuộc tụ tập công cộng, biểu tình, tuần hành, bãi công hoặc bạo loạn mang tính chất phản kháng/chính trị.\n- Ví dụ: biểu tình, tuần hành, bãi công, đình công, xuống đường, tụ tập phản đối.",
    "Contact:Meet": "Một cuộc gặp gỡ trực tiếp, hội nghị, họp hành, tiếp xúc ngoại giao hoặc tập hợp vật lý của mọi người.\n- Ví dụ: họp, gặp gỡ, hội chẩn, hội nghị, tiếp kiến, hội đàm, gặp mặt.",
    "Contact:Phone-Write": "Liên lạc giữa hai hoặc nhiều bên không trực tiếp, thông qua điện thoại, thư từ, email, văn bản hoặc tin nhắn.\n- Ví dụ: gọi điện, gửi thư, gửi email, nhắn tin, gửi công văn, liên lạc qua điện thoại.",
    "Personnel:Start-Position": "Một người bắt đầu một công việc, chức vụ, vị trí hoặc chức danh chính thức mới trong một tổ chức/chính phủ.\n- Ví dụ: bổ nhiệm, nhậm chức, nhận chức, vào làm, ký hợp đồng lao động, tuyển dụng, phong hàm.",
    "Personnel:End-Position": "Một người rời bỏ, từ chức, bị sa thải, cách chức hoặc về hưu khỏi một công việc, vị trí hoặc chức danh.\n- Ví dụ: từ chức, sa thải, cách chức, miễn nhiệm, nghỉ hưu, thôi việc, bị đuổi việc.",
    "Personnel:Nominate": "Một người chính thức được đề cử, đề xuất hoặc giới thiệu vào một vị trí, giải thưởng hoặc chức danh.\n- Ví dụ: đề cử, giới thiệu ứng cử, ứng cử, tiến cử.",
    "Personnel:Elect": "Một người chính thức được bầu chọn, trúng cử vào một vị trí, văn phòng hoặc chức danh thông qua bỏ phiếu.\n- Ví dụ: trúng cử, đắc cử, bầu, bầu chọn, bỏ phiếu bầu.",
    "Justice:Arrest-Jail": "Một người bị bắt giữ, tạm giữ, tạm giam hoặc bỏ tù bởi cơ quan thực thi pháp luật.\n- Ví dụ: bắt, bắt giữ, tạm giam, bớ, xích, tống giam, áp giải về đồn (khi bắt đầu giam giữ).",
    "Justice:Release-Parole": "Một người được thả tự do từ nhà tù, trại tạm giam, hết hạn tù hoặc được cho tại ngoại, hưởng án treo.\n- Ví dụ: thả, trả tự do, đặc xá (phần ra tù), tại ngoại, mãn hạn tù.",
    "Justice:Trial-Hearing": "Một phiên tòa xét xử, buổi điều trần, tranh tụng hoặc thủ tục tố tụng pháp lý chính thức tại tòa.\n- Ví dụ: xét xử, hầu tòa, phiên tòa, mở tòa, điều trần, ra tòa.",
    "Justice:Charge-Indict": "Một người hoặc tổ chức bị cơ quan chức năng chính thức khởi tố, buộc tội, truy tố hoặc ban hành cáo trạng.\n- Ví dụ: khởi tố, truy tố, buộc tội, cáo buộc, ban hành cáo trạng.",
    "Justice:Sue": "Một cá nhân hoặc tổ chức đệ đơn kiện dân sự, khởi kiện đòi bồi thường chống lại một bên khác tại tòa.\n- Ví dụ: kiện, khởi kiện, đâm đơn kiện, kiện ra tòa.",
    "Justice:Convict": "Bị cáo chính thức bị tòa án tuyên bố là có tội (trước khi hoặc đi kèm với việc tuyên án).\n- Ví dụ: tuyên án có tội, kết tội, bị kết án, khẳng định phạm tội.",
    "Justice:Sentence": "Bị cáo chính thức bị tòa án tuyên phạt một hình phạt hoặc một mức án cụ thể (án tù, tử hình, tù treo).\n- Ví dụ: tuyên phạt, phạt tù, tuyên án tử hình, phạt 5 năm tù, tuyên mức án.\n- Lưu ý: Trích xuất động từ hoặc cụm từ biểu thị hành động tuyên phạt của tòa.",
    "Justice:Fine": "Bị cáo hoặc tổ chức bị cơ quan có thẩm quyền ra phán quyết bắt buộc phải nộp tiền phạt như một hình phạt pháp lý.\n- Ví dụ: xử phạt hành chính, phạt tiền, ra quyết định phạt, phạt 10 triệu đồng.\n- Lưu ý: Nếu câu ghi \"bị phạt 50 triệu\", từ \"phạt\" chính là trigger của Justice:Fine.",
    "Justice:Execute": "Một người bị thi hành án tử hình dựa trên quyết định pháp lý của tòa án.\n- Ví dụ: thi hành án tử hình, tiêm thuốc độc, xử bắn, tử hình (hành động thực thi).",
    "Justice:Extradite": "Một người bị dẫn độ, bàn giao từ quốc gia/vùng lãnh thổ này sang quốc gia/vùng lãnh thổ khác để xử lý pháp lý.\n- Ví dụ: dẫn độ, bàn giao tội phạm quốc tế, trục xuất và dẫn độ.",
    "Justice:Acquit": "Bị cáo chính thức được tòa tuyên trắng án, vô tội hoặc hủy bỏ các cáo buộc hình sự.\n- Ví dụ: tuyên trắng án, tuyên vô tội, đình chỉ vụ án đối với bị can (vì không phạm tội).",
    "Justice:Pardon": "Một người chính thức được nguyên thủ quốc gia đặc xá, ân xá, tha tù trước thời hạn hoặc xóa án tích.\n- Ví dụ: đặc xá, ân xá, chủ tịch nước xá tội.",
    "Justice:Appeal": "Một đơn kháng cáo hoặc hành động kháng cáo được đệ trình để chống lại phán quyết hiện tại của tòa án.\n- Ví dụ: kháng cáo, làm đơn kháng cáo, chống án."
}

ARGUMENT_TYPES = {
    "Place": "Địa điểm nơi sự kiện diễn ra.\n\nVí dụ: tại Hà Nội, ở quận 1, tại hiện trường, ở ngã tư, tại trụ sở công ty.\n\nLƯU Ý: Phải là địa điểm trực tiếp gắn liền với không gian xảy ra hành vi của trigger.",
    "Time": "Thời gian hoặc ngày tháng khi sự kiện diễn ra.\n\nVí dụ: ngày 26/11, hôm qua, lúc 14h, năm 2026, suốt 3 tiếng.\n\nLƯU Ý: Trích xuất toàn bộ mốc hoặc khoảng thời gian đóng vai trò là thời điểm xảy ra sự kiện.",
    "Person": "Cá nhân tham gia hoặc chịu tác động từ sự kiện nói chung (khi không thuộc các vai trò cụ thể hơn như Victim, Agent, Defendant...).\n\nVí dụ: các hành khách, những người xung quanh, anh A (trong sự kiện kết hôn/sinh con).",
    "Agent": "Chủ thể chủ động, cá nhân hoặc tổ chức khởi xướng, thực hiện hoặc gây ra sự kiện.\n\nVí dụ:\n- Công ty A thành lập chi nhánh -> Agent: Công ty A\n- Bộ trưởng bổ nhiệm cán bộ -> Agent: Bộ trưởng\n- Ông B chuyển tiền -> Agent: Ông B\n\nLƯU Ý: Không dùng Agent cho các sự kiện bạo lực (dùng Attacker) hoặc tố tụng pháp lý (dùng Prosecutor/Adjudicator).",
    "Victim": "Nạn nhân — người bị tổn hại, bị thương, bị tác động tiêu cực hoặc tử vong trong sự kiện.\n\nVí dụ: người đi đường bị tông, nạn nhân bị đâm, các hành khách bị thiệt mạng.",
    "Instrument": "Công cụ, vũ khí, thiết bị hoặc phương tiện được sử dụng trực tiếp để thực hiện hành vi trong sự kiện.\n\nVí dụ: đâm bằng dao -> Instrument: dao; dùng súng bắn -> Instrument: súng; dùng bom xăng tấn công -> Instrument: bom xăng.",
    "Artifact": "Vật thể vật lý, vũ khí, phương tiện hoặc tổ chức được vận chuyển, di chuyển hoặc chuyển nhượng quyền sở hữu.\n\nVí dụ:\n- Vận chuyển 10 bánh heroin -> Artifact: 10 bánh heroin\n- Sang nhượng lại cửa hàng -> Artifact: cửa hàng\n- Áp giải bị can -> Artifact: bị can",
    "Vehicle": "Phương tiện di chuyển được sử dụng để thực hiện việc vận chuyển hoặc đi lại.\n\nVí dụ: chở bằng xe tải -> Vehicle: xe tải; bay đến bằng trực thăng -> Vehicle: trực thăng.",
    "Price": "Số tiền hoặc giá trị tiền tệ quy định cho một giao dịch mua bán hoặc chi phí vận chuyển.\n\nVí dụ: mua nhà với giá 5 tỷ -> Price: 5 tỷ; giá vé 500 nghìn đồng -> Price: 500 nghìn đồng.",
    "Origin": "Điểm xuất phát, nguồn gốc hoặc vị trí bắt đầu của một chuyển động, hành trình hoặc quá trình vận chuyển.\n\nVí dụ: đi từ Hải Phòng -> Origin: Hải Phòng; xuất phát từ biên giới -> Origin: biên giới.",
    "Destination": "Điểm đến, đích đến hoặc vị trí kết thúc của một chuyển động, hành trình hoặc quá trình vận chuyển.\n\nVí dụ: bay đến Hà Nội -> Destination: Hà Nội; chuyển hàng về kho -> Destination: kho.",
    "Buyer": "Cá nhân, tổ chức hoặc thực thể thực hiện hành vi mua một tài sản, cổ phần hoặc tổ chức.\n\nVí dụ: ông A tậu xe mới -> Buyer: ông A; Tập đoàn X mua lại công ty Y -> Buyer: Tập đoàn X.",
    "Seller": "Cá nhân, tổ chức hoặc thực thể thực hiện hành vi bán hoặc chuyển nhượng một tài sản, cổ phần hoặc tổ chức.\n\nVí dụ: cửa hàng bán điện thoại -> Seller: cửa hàng; bà B sang nhượng đất -> Seller: bà B.",
    "Beneficiary": "Cá nhân hoặc tổ chức được hưởng lợi từ một giao dịch tài chính, chuyển nhượng hoặc tài trợ.\n\nVí dụ: quyên góp cho đồng bào miền Trung -> Beneficiary: đồng bào miền Trung; tài trợ cho dự án X -> Beneficiary: dự án X.",
    "Giver": "Cá nhân hoặc tổ chức thực hiện việc chuyển, cho, vay, quyên góp, gửi tiền hoặc trả tiền.\n\nVí dụ: Ngân hàng giải ngân -> Giver: Ngân hàng; anh X nộp tiền phạt -> Giver: anh X.",
    "Recipient": "Cá nhân hoặc tổ chức nhận tiền, khoản vay, tiền phạt hoặc tài chính từ bên khác.\n\nVí dụ: nhận tiền bồi thường -> Recipient: người nhận; nộp tiền vào ngân sách nhà nước -> Recipient: ngân sách nhà nước.",
    "Money": "Khoản tiền hoặc mệnh giá tiền tệ cụ thể xuất hiện trong giao dịch tài chính hoặc hình phạt tiền.\n\nVí dụ: chuyển khoản 200 triệu -> Money: 200 triệu; phạt 10 triệu đồng -> Money: 10 triệu đồng.",
    "Organization": "Tổ chức, công ty hoặc cơ quan bị tác động trực tiếp bởi các sự kiện kinh doanh doanh nghiệp (như thành lập, sáp nhập, giải thể, phá sản).\n\nVí dụ: thành lập Công ty ABC -> Organization: Công ty ABC; sáp nhập hai ngân hàng -> Organization: hai ngân hàng.",
    "Attacker": "Cá nhân, nhóm người, tổ chức hoặc quốc gia chủ động khơi mào, thực hiện hành vi bạo lực, tấn công vũ trang hoặc hành hung.\n\nVí dụ: đối tượng cầm dao đâm -> Attacker: đối tượng; quân đội oanh tạc -> Attacker: quân đội.",
    "Target": "Mục tiêu (người, tổ chức, phương tiện, cơ sở hạ tầng hoặc địa điểm) bị nhắm đến trong một cuộc tấn công hoặc hành vi bạo lực.\n\nVí dụ: xả súng vào đám đông -> Target: đám đông; ném bom vào tòa nhà -> Target: tòa nhà.",
    "Entity": "Các bên tham gia trực tiếp, người giao tiếp hoặc người biểu tình trong các sự kiện gặp gỡ, liên lạc hoặc biểu tình tuần hành.\n\nVí dụ: cuộc gặp giữa Thủ tướng và Tổng thống -> Entity: Thủ tướng, Tổng thống; hàng ngàn người xuống đường -> Entity: hàng ngàn người.",
    "Position": "Chức danh nghề nghiệp, vị trí công tác, chức vụ chính thức liên quan đến sự kiện nhân sự.\n\nVí dụ: bổ nhiệm làm Giám đốc -> Position: Giám đốc; từ chức Thủ tướng -> Position: Thủ tướng.",
    "Defendant": "Bị cáo, bị can, người hoặc tổ chức bị cáo buộc, bị khởi tố, bắt giữ hoặc xét xử trong các thủ tục tố tụng pháp lý.\n\nVí dụ: bắt giữ đối tượng A -> Defendant: đối tượng A; xét xử bị cáo B -> Defendant: bị cáo B.",
    "Prosecutor": "Cơ quan, lực lượng chức năng, viện kiểm sát hoặc người đại diện pháp luật thực hiện việc cáo buộc, truy tố hoặc bắt giữ.\n\nVí dụ: Viện kiểm sát truy tố -> Prosecutor: Viện kiểm sát; Công an bắt quả tang -> Prosecutor: Công an.",
    "Adjudicator": "Thẩm phán, hội đồng xét xử, tòa án hoặc cơ quan có thẩm quyền ra phán quyết pháp lý cuối cùng.\n\nVí dụ: Tòa án nhân dân tuyên phạt -> Adjudicator: Tòa án nhân dân; Hội đồng xét xử khẳng định -> Adjudicator: Hội đồng xét xử.",
    "Crime": "Tội danh, hành vi vi phạm pháp luật hoặc cáo buộc cụ thể là nguyên nhân dẫn đến việc bắt giữ, xét xử, khởi tố hoặc tuyên án.\n\nVí dụ: khởi tố tội lừa đảo -> Crime: lừa đảo; bị bắt vì tội trộm cắp -> Crime: trộm cắp.",
    "Sentence": "Hình phạt pháp lý, mức án cụ thể do tòa án tuyên phạt.\n\nVí dụ: tuyên phạt 10 năm tù -> Sentence: 10 năm tù; án tử hình -> Sentence: án tử hình.",
    "Plaintiff": "Nguyên đơn — cá nhân hoặc tổ chức đệ đơn kiện dân sự, khởi kiện đòi bồi thường chống lại bị đơn tại tòa.\n\nVí dụ: ông A làm đơn kiện công ty B -> Plaintiff: ông A."
}

EVENT_ARGUMENTS_SCHEMA = {
    "Life:Be-Born": {
        "schema": {
            "Person": [
                "Person"
            ],
            "Time": [
                "Time"
            ],
            "Place": [
                "Geopolitical-Entity",
                "Location",
                "Facility"
            ]
        }
    },
    "Life:Marry": {
        "schema": {
            "Person": [
                "Person"
            ],
            "Time": [
                "Time"
            ],
            "Place": [
                "Geopolitical-Entity",
                "Location",
                "Facility"
            ]
        }
    },
    "Life:Divorce": {
        "schema": {
            "Person": [
                "Person"
            ],
            "Time": [
                "Time"
            ],
            "Place": [
                "Geopolitical-Entity",
                "Location",
                "Facility"
            ]
        }
    },
    "Life:Injure": {
        "schema": {
            "Agent": [
                "Person",
                "Organization",
                "Geopolitical-Entity"
            ],
            "Victim": [
                "Person"
            ],
            "Instrument": [
                "Weapon",
                "Vehicle"
            ],
            "Time": [
                "Time"
            ],
            "Place": [
                "Geopolitical-Entity",
                "Location",
                "Facility"
            ]
        }
    },
    "Life:Die": {
        "schema": {
            "Agent": [
                "Person",
                "Organization",
                "Geopolitical-Entity"
            ],
            "Victim": [
                "Person"
            ],
            "Instrument": [
                "Weapon",
                "Vehicle"
            ],
            "Time": [
                "Time"
            ],
            "Place": [
                "Geopolitical-Entity",
                "Location",
                "Facility"
            ]
        }
    },
    "Movement:Transport": {
        "schema": {
            "Agent": [
                "Person",
                "Organization",
                "Geopolitical-Entity"
            ],
            "Artifact": [
                "Person",
                "Weapon",
                "Vehicle"
            ],
            "Vehicle": [
                "Vehicle"
            ],
            "Price": [
                "Number"
            ],
            "Origin": [
                "Geopolitical-Entity",
                "Location",
                "Facility"
            ],
            "Destination": [
                "Geopolitical-Entity",
                "Location",
                "Facility"
            ],
            "Time": [
                "Time"
            ]
        }
    },
    "Transaction:Transfer-Ownership": {
        "schema": {
            "Buyer": [
                "Person",
                "Organization",
                "Geopolitical-Entity"
            ],
            "Seller": [
                "Person",
                "Organization",
                "Geopolitical-Entity"
            ],
            "Beneficiary": [
                "Person",
                "Organization",
                "Geopolitical-Entity"
            ],
            "Artifact": [
                "Vehicle",
                "Weapon",
                "Facility",
                "Organization"
            ],
            "Price": [
                "Money"
            ],
            "Time": [
                "Time"
            ],
            "Place": [
                "Geopolitical-Entity",
                "Location",
                "Facility"
            ]
        }
    },
    "Transaction:Transfer-Money": {
        "schema": {
            "Giver": [
                "Person",
                "Organization",
                "Geopolitical-Entity"
            ],
            "Recipient": [
                "Person",
                "Organization",
                "Geopolitical-Entity"
            ],
            "Beneficiary": [
                "Person",
                "Organization",
                "Geopolitical-Entity"
            ],
            "Money": [
                "Money"
            ],
            "Time": [
                "Time"
            ],
            "Place": [
                "Geopolitical-Entity",
                "Location",
                "Facility"
            ]
        }
    },
    "Business:Start-Organization": {
        "schema": {
            "Agent": [
                "Person",
                "Organization",
                "Geopolitical-Entity"
            ],
            "Organization": [
                "Organization"
            ],
            "Time": [
                "Time"
            ],
            "Place": [
                "Geopolitical-Entity",
                "Location",
                "Facility"
            ]
        }
    },
    "Business:Merge-Organization": {
        "schema": {
            "Organization": [
                "Organization"
            ],
            "Time": [
                "Time"
            ],
            "Place": [
                "Geopolitical-Entity",
                "Location",
                "Facility"
            ]
        }
    },
    "Business:Declare-Bankruptcy": {
        "schema": {
            "Organization": [
                "Organization",
                "Person",
                "Geopolitical-Entity"
            ],
            "Time": [
                "Time"
            ],
            "Place": [
                "Geopolitical-Entity",
                "Location",
                "Facility"
            ]
        }
    },
    "Business:End-Organization": {
        "schema": {
            "Organization": [
                "Organization"
            ],
            "Time": [
                "Time"
            ],
            "Place": [
                "Geopolitical-Entity",
                "Location",
                "Facility"
            ]
        }
    },
    "Conflict:Attack": {
        "schema": {
            "Attacker": [
                "Person",
                "Organization",
                "Geopolitical-Entity"
            ],
            "Target": [
                "Person",
                "Organization",
                "Vehicle",
                "Facility",
                "Weapon"
            ],
            "Instrument": [
                "Weapon",
                "Vehicle"
            ],
            "Time": [
                "Time"
            ],
            "Place": [
                "Geopolitical-Entity",
                "Location",
                "Facility"
            ]
        }
    },
    "Conflict:Demonstrate": {
        "schema": {
            "Entity": [
                "Person",
                "Organization"
            ],
            "Time": [
                "Time"
            ],
            "Place": [
                "Location",
                "Geopolitical-Entity",
                "Facility"
            ]
        }
    },
    "Contact:Meet": {
        "schema": {
            "Entity": [
                "Person",
                "Organization",
                "Geopolitical-Entity"
            ],
            "Time": [
                "Time"
            ],
            "Place": [
                "Geopolitical-Entity",
                "Location",
                "Facility"
            ]
        }
    },
    "Contact:Phone-Write": {
        "schema": {
            "Entity": [
                "Person",
                "Organization",
                "Geopolitical-Entity"
            ],
            "Time": [
                "Time"
            ]
        }
    },
    "Personnel:Start-Position": {
        "schema": {
            "Person": [
                "Person"
            ],
            "Entity": [
                "Organization",
                "Geopolitical-Entity"
            ],
            "Position": [
                "Job"
            ],
            "Time": [
                "Time"
            ],
            "Place": [
                "Geopolitical-Entity",
                "Location",
                "Facility"
            ]
        }
    },
    "Personnel:End-Position": {
        "schema": {
            "Person": [
                "Person"
            ],
            "Entity": [
                "Organization",
                "Geopolitical-Entity"
            ],
            "Position": [
                "Job"
            ],
            "Time": [
                "Time"
            ],
            "Place": [
                "Geopolitical-Entity",
                "Location",
                "Facility"
            ]
        }
    },
    "Personnel:Nominate": {
        "schema": {
            "Person": [
                "Person"
            ],
            "Agent": [
                "Person",
                "Organization",
                "Geopolitical-Entity",
                "Facility"
            ],
            "Position": [
                "Job"
            ],
            "Time": [
                "Time"
            ],
            "Place": [
                "Geopolitical-Entity",
                "Location",
                "Facility"
            ]
        }
    },
    "Personnel:Elect": {
        "schema": {
            "Person": [
                "Person"
            ],
            "Entity": [
                "Person",
                "Organization",
                "Geopolitical-Entity"
            ],
            "Position": [
                "Job"
            ],
            "Time": [
                "Time"
            ],
            "Place": [
                "Geopolitical-Entity",
                "Location",
                "Facility"
            ]
        }
    },
    "Justice:Arrest-Jail": {
        "schema": {
            "Person": [
                "Person"
            ],
            "Agent": [
                "Person",
                "Organization",
                "Geopolitical-Entity"
            ],
            "Crime": [
                "Crime"
            ],
            "Time": [
                "Time"
            ],
            "Place": [
                "Geopolitical-Entity",
                "Location",
                "Facility"
            ]
        }
    },
    "Justice:Release-Parole": {
        "schema": {
            "Person": [
                "Person"
            ],
            "Entity": [
                "Person",
                "Organization",
                "Geopolitical-Entity"
            ],
            "Crime": [
                "Crime"
            ],
            "Time": [
                "Time"
            ],
            "Place": [
                "Geopolitical-Entity",
                "Location",
                "Facility"
            ]
        }
    },
    "Justice:Trial-Hearing": {
        "schema": {
            "Defendant": [
                "Person",
                "Organization",
                "Geopolitical-Entity"
            ],
            "Prosecutor": [
                "Person",
                "Organization",
                "Geopolitical-Entity"
            ],
            "Adjudicator": [
                "Person",
                "Organization",
                "Geopolitical-Entity"
            ],
            "Crime": [
                "Crime"
            ],
            "Time": [
                "Time"
            ],
            "Place": [
                "Geopolitical-Entity",
                "Location",
                "Facility"
            ]
        }
    },
    "Justice:Charge-Indict": {
        "schema": {
            "Defendant": [
                "Person",
                "Organization",
                "Geopolitical-Entity"
            ],
            "Prosecutor": [
                "Person",
                "Organization",
                "Geopolitical-Entity"
            ],
            "Adjudicator": [
                "Person",
                "Organization",
                "Geopolitical-Entity"
            ],
            "Crime": [
                "Crime"
            ],
            "Time": [
                "Time"
            ],
            "Place": [
                "Geopolitical-Entity",
                "Location",
                "Facility"
            ]
        }
    },
    "Justice:Sue": {
        "schema": {
            "Plaintiff": [
                "Person",
                "Organization",
                "Geopolitical-Entity"
            ],
            "Defendant": [
                "Person",
                "Organization",
                "Geopolitical-Entity"
            ],
            "Adjudicator": [
                "Person",
                "Organization",
                "Geopolitical-Entity"
            ],
            "Crime": [
                "Crime"
            ],
            "Time": [
                "Time"
            ],
            "Place": [
                "Geopolitical-Entity",
                "Location",
                "Facility"
            ]
        }
    },
    "Justice:Convict": {
        "schema": {
            "Defendant": [
                "Person",
                "Organization",
                "Geopolitical-Entity"
            ],
            "Adjudicator": [
                "Person",
                "Organization",
                "Geopolitical-Entity"
            ],
            "Crime": [
                "Crime"
            ],
            "Time": [
                "Time"
            ],
            "Place": [
                "Geopolitical-Entity",
                "Location",
                "Facility"
            ]
        }
    },
    "Justice:Sentence": {
        "schema": {
            "Defendant": [
                "Person",
                "Organization",
                "Geopolitical-Entity"
            ],
            "Adjudicator": [
                "Person",
                "Organization",
                "Geopolitical-Entity"
            ],
            "Crime": [
                "Crime"
            ],
            "Sentence": [
                "Sentence"
            ],
            "Time": [
                "Time"
            ],
            "Place": [
                "Geopolitical-Entity",
                "Location",
                "Facility"
            ]
        }
    },
    "Justice:Fine": {
        "schema": {
            "Entity": [
                "Person",
                "Organization",
                "Geopolitical-Entity"
            ],
            "Adjudicator": [
                "Person",
                "Organization",
                "Geopolitical-Entity"
            ],
            "Money": [
                "Number"
            ],
            "Crime": [
                "Crime"
            ],
            "Time": [
                "Time"
            ],
            "Place": [
                "Geopolitical-Entity",
                "Location",
                "Facility"
            ]
        }
    },
    "Justice:Execute": {
        "schema": {
            "Person": [
                "Person"
            ],
            "Agent": [
                "Person",
                "Organization",
                "Geopolitical-Entity"
            ],
            "Crime": [
                "Crime"
            ],
            "Time": [
                "Time"
            ],
            "Place": [
                "Geopolitical-Entity",
                "Location",
                "Facility"
            ]
        }
    },
    "Justice:Extradite": {
        "schema": {
            "Agent": [
                "Person",
                "Organization",
                "Geopolitical-Entity"
            ],
            "Person": [
                "Person"
            ],
            "Destination": [
                "Geopolitical-Entity",
                "Location",
                "Facility"
            ],
            "Origin": [
                "Geopolitical-Entity",
                "Location",
                "Facility"
            ],
            "Crime": [
                "Crime"
            ],
            "Time": [
                "Time"
            ]
        }
    },
    "Justice:Acquit": {
        "schema": {
            "Defendant": [
                "Person",
                "Organization",
                "Geopolitical-Entity"
            ],
            "Adjudicator": [
                "Person",
                "Organization",
                "Geopolitical-Entity"
            ],
            "Crime": [
                "Crime"
            ],
            "Time": [
                "Time"
            ],
            "Place": [
                "Geopolitical-Entity",
                "Location",
                "Facility"
            ]
        }
    },
    "Justice:Pardon": {
        "schema": {
            "Defendant": [
                "Person",
                "Organization",
                "Geopolitical-Entity"
            ],
            "Adjudicator": [
                "Person",
                "Organization",
                "Geopolitical-Entity"
            ],
            "Crime": [
                "Crime"
            ],
            "Time": [
                "Time"
            ],
            "Place": [
                "Geopolitical-Entity",
                "Location",
                "Facility"
            ]
        }
    },
    "Justice:Appeal": {
        "schema": {
            "Defendant": [
                "Person",
                "Organization",
                "Geopolitical-Entity"
            ],
            "Prosecutor": [
                "Person",
                "Organization",
                "Geopolitical-Entity"
            ],
            "Adjudicator": [
                "Person",
                "Organization",
                "Geopolitical-Entity"
            ],
            "Crime": [
                "Crime"
            ],
            "Time": [
                "Time"
            ],
            "Place": [
                "Geopolitical-Entity",
                "Location",
                "Facility"
            ]
        }
    }
}

ENTITIES_SYSTEM_PROMPT_TEMPLATE = """Bạn là một trợ lý AI nhận dạng thực thể cho văn bản tiếng Việt.
Nhiệm vụ của bạn là xác định và trích xuất TẤT CẢ các đề cập thực thể từ câu tiếng Việt đã cho.

## CÁC LOẠI THỰC THỂ:
{entity_types_text}
    
## QUY TẮC TRÍCH XUẤT:
1. Không trực tiếp trả về kết quả JSON, thực hiện suy luận từng bước:
    - Bước 1: Xác định toàn bộ span text ứng viên thực thể.
    - Bước 2: Đối với mỗi ứng viên, chọn ra một loại thực thể phù hợp nhất. Nêu ra lý do tại sao loại thực thể này lại phù hợp hơn những loại khác.
    - Bước 3: Kết luận và đưa kết quả JSON.
2. Khi không chắc chắn về việc một từ hoặc cụm từ có phải thực thể hay không, HÃY TRÍCH XUẤT NÓ, TUYỆT ĐỐI KHÔNG BỎ SÓT.
3. Trích xuất span text của thực thể CHÍNH XÁC như trong câu — không sửa đổi, rút gọn hay dịch.
4. Nếu không tìm thấy thực thể nào, trả về danh sách rỗng.

## ĐỊNH DẠNG ĐẦU RA:
[QUÁ TRÌNH SUY LUẬN TỪNG BƯỚC]

{{
  "entities": [
    {{"text": "span text chính xác từ câu gốc", "type": "loại thực thể"}}
  ]
}}
"""

EVENTS_SYSTEM_PROMPT_TEMPLATE = """Bạn là một trợ lý AI nhận dạng sự kiện cho văn bản tiếng Việt.
Nhiệm vụ của bạn là xác định và trích xuất TẤT CẢ các trigger (từ hoặc cụm từ biểu thị sự kiện) từ câu tiếng Việt đã cho.

## CÁC LOẠI SỰ KIỆN:
{event_types_text}

## QUY TẮC TRÍCH XUẤT:
1. Không trực tiếp trả về kết quả JSON, thực hiện suy luận từng bước:
    - Bước 1: Xác định toàn bộ span text ứng viên trigger.
    - Bước 2: Đối với mỗi ứng viên, chọn ra một loại sự kiện phù hợp nhất. Nêu ra lý do tại sao loại sự kiện này lại phù hợp hơn những loại khác.
    - Bước 3: Kết luận và đưa kết quả JSON.
2. Khi không chắc chắn về việc một từ hoặc cụm từ có phải trigger hay không, HÃY TRÍCH XUẤT NÓ, TUYỆT ĐỐI KHÔNG BỎ SÓT.
3. Trích xuất trigger tối thiểu (chỉ chấp nhận động từ), hành động biểu thị sự kiện hợp lệ — phải xuất hiện nguyên văn trong câu, không sửa đổi hay dịch.
4. Nếu không tìm thấy sự kiện nào, trả về danh sách rỗng.

## ĐỊNH DẠNG ĐẦU RA:
[QUÁ TRÌNH SUY LUẬN TỪNG BƯỚC]

{{
  "events": [
    {{"trigger": "span text trigger chính xác từ câu gốc", "type": "loại sự kiện"}}
  ]
}}
"""

EVENT_ARGUMENTS_SYSTEM_PROMPT_TEMPLATE = """Bạn là một trợ lý AI gán vai trò thực thể trong sự kiện cho văn bản tiếng Việt.
Nhiệm vụ của bạn: cho trước một câu, loại sự kiện, trigger (từ/cụm động từ kích hoạt sự kiện) của nó, danh sách thực thể ứng viên, danh sách loại tham số hợp lệ cho sự kiện — hãy chọn những thực thể phù hợp với sự kiện, sau đó gán loại tham số sự kiện cho thực thể này.

## QUY TẮC GÁN:
1. Không trực tiếp trả về kết quả JSON, thực hiện suy luận từng bước:
    - Bước 1: Xác định các ứng viên thực thể liên quan tới sự kiện thông qua mối quan hệ với trigger.
    - Bước 2: Đối với mỗi thực thể trên, chọn ra một loại tham số phù hợp nhất. Nêu ra lý do tại sao loại tham số này lại phù hợp hơn những loại khác.
    - Bước 3: Kết luận và đưa kết quả JSON.
2. Thực thể liên kết trực tiếp với trigger qua quan hệ chủ ngữ, tân ngữ trực tiếp, trạng ngữ hoặc bổ ngữ giới từ là ứng viên mạnh — gán nếu loại tham số hợp lệ.
3. Cũng cho phép thực thể có vai trò ngữ nghĩa rõ ràng và tự nhiên liên quan đến sự kiện, dù liên kết ngữ pháp hơi gián tiếp, miễn là thực thể đó đóng vai trò tham số đó một cách hợp lý trong ngữ cảnh sự kiện mô tả trong câu.
4. Loại bỏ thực thể nếu nó chủ yếu thuộc về một sự kiện/động từ khác trong câu, hoặc nếu liên kết với trigger này cần suy luận nhiều bước mà không có cơ sở văn bản trực tiếp.
5. Gán mỗi thực thể được chọn đúng một loại tham số sự kiện hợp lệ.

## ĐỊNH DẠNG ĐẦU RA:
[QUÁ TRÌNH SUY LUẬN TỪNG BƯỚC]

{
  "arguments": [
    {"text": "văn bản chính xác khớp với thực thể ứng viên", "type": "loại chính xác từ danh sách hợp lệ"}
  ]
}
"""

FULL_SYSTEM_PROMPT_TEMPLATE = """Bạn là một trợ lý AI trích xuất thực thể, sự kiện từ văn bản tiếng Việt và gán loại tham số sự kiện cho các thực thể tham gia vào từng sự kiện.
Nhiệm vụ của bạn là xác định và trích xuất TẤT CẢ thực thể kèm span text, trigger (từ/cụm động từ kích hoạt) sự kiện và tham số tương ứng của từng thực thể từ câu tiếng Việt đã cho.

## CÁC LOẠI THỰC THỂ:
{entity_types_text}

## CÁC LOẠI SỰ KIỆN:
{event_types_text}

## CÁC LOẠI THAM SỐ:
{argument_types_text}

## QUY TẮC TRÍCH XUẤT THỰC THỂ
1. Khi không chắc chắn về việc một từ hoặc cụm từ có phải thực thể hay không, HÃY TRÍCH XUẤT NÓ, TUYỆT ĐỐI KHÔNG BỎ SÓT.
2. Trích xuất span text của thực thể CHÍNH XÁC như trong câu — không sửa đổi, rút gọn hay dịch.
3. Nếu không tìm thấy thực thể nào, trả về danh sách rỗng.

## QUY TẮC TRÍCH XUẤT SỰ KIỆN
1. Khi không chắc chắn về việc một từ hoặc cụm từ có phải trigger hay không, HÃY TRÍCH XUẤT NÓ, TUYỆT ĐỐI KHÔNG BỎ SÓT.
2. Trích xuất trigger tối thiểu (chỉ chấp nhận động từ), hành động biểu thị sự kiện hợp lệ — phải xuất hiện nguyên văn trong câu, không sửa đổi hay dịch.
3. Nếu không tìm thấy sự kiện nào, trả về danh sách rỗng.

## QUY TẮC GÁN THAM SỐ SỰ KIỆN:
1. Thực thể liên kết trực tiếp với trigger qua quan hệ chủ ngữ, tân ngữ trực tiếp, trạng ngữ hoặc bổ ngữ giới từ là ứng viên mạnh — gán nếu loại tham số hợp lệ.
2. Cũng cho phép thực thể có vai trò ngữ nghĩa rõ ràng và tự nhiên liên quan đến sự kiện, dù liên kết ngữ pháp hơi gián tiếp, miễn là thực thể đó đóng vai trò tham số đó một cách hợp lý trong ngữ cảnh sự kiện mô tả trong câu.
3. Loại bỏ thực thể nếu nó chủ yếu thuộc về một sự kiện/động từ khác trong câu, hoặc nếu liên kết với trigger này cần suy luận nhiều bước mà không có cơ sở văn bản trực tiếp.
4. Gán mỗi thực thể được chọn đúng một loại tham số sự kiện hợp lệ.

## QUY TẮC CHUNG
1. Không trực tiếp trả về kết quả JSON, thực hiện suy luận từng bước:
    - Bước 1: Xác định tất cả thực thể có trong câu và loại tương ứng.
    - Bước 2: Xác định tất cả trigger sự kiện có trong câu và loại tương ứng.
    - Bước 3: Đối với mỗi trigger sự kiện, xác định tất cả thực thể có vai trò tham số tương ứng và loại tham số tương ứng.
    - Bước 4: Kết luận và đưa kết quả JSON.

## ĐỊNH DẠNG ĐẦU RA (chỉ JSON thuần túy):
{{
  "entities": [
    {{"text": "văn bản thực thể chính xác", "type": "entity_type"}}
  ],
  "events": [
    {{
      "type": "event_type",
      "trigger": "văn bản trigger chính xác",
      "arguments": [
        {{"text": "văn bản thực thể chính xác", "type": "argument_type"}}
      ]
    }}
  ]
}}
"""


ENTITIES_BUILDER_SYSTEM_PROMPT_TEMPLATE = """Bạn là một trợ lý AI tạo dữ liệu huấn luyện (dataset builder) nhận dạng thực thể cho tiếng Việt.
Nhiệm vụ của bạn là viết một quá trình suy luận từng bước tự nhiên giải thích lý do trích xuất các thực thể cụ thể từ câu tiếng Việt, sau đó trả về kết quả JSON chứa các thực thể này.

Bạn sẽ được cung cấp:
1. Một câu tiếng Việt.
2. Danh sách các thực thể mục tiêu cần phải trích xuất (đây là nhãn đúng).

## CÁC LOẠI THỰC THỂ:
{entity_types_text}
    
## QUY TẮC BẮT BUỘC KHI SINH SUY LUẬN:
1. TRONG BÀI VIẾT SUY LUẬN, TUYỆT ĐỐI KHÔNG ĐƯỢC ĐẢ ĐỘNG đến các từ ngữ và khái niệm liên quan đến việc có dữ liệu cho trước, ví dụ: "GOLD", "mục tiêu", "cho trước", "yêu cầu", "nhãn", "trùng khớp", "danh sách", v.v. Hãy viết như thể bạn tự phân tích câu và tự phát hiện ra chúng từ đầu.
2. Hãy viết suy luận dưới góc nhìn của một mô hình đang tự mình phân tích và trích xuất thực thể từ câu gốc một cách tự nhiên từ đầu:
    - Bước 1: Xác định toàn bộ các thực thể ứng viên có trong câu.
    - Bước 2: Phân tích ngữ cảnh và định nghĩa loại thực thể để giải thích vì sao loại thực thể đó là phù hợp nhất cho từng thực thể.
    - Bước 3: Đưa ra định dạng JSON kết quả chứa các thực thể này.
3. Phần JSON kết quả phải khớp hoàn toàn với danh sách thực thể mục tiêu được cung cấp.

## ĐỊNH DẠNG ĐẦU RA (Không thêm bất kỳ từ ngữ nào ngoài định dạng này):
[QUÁ TRÌNH SUY LUẬN TỪNG BƯỚC]

<tiến trình suy luận tự nhiên, không nhắc đến việc có dữ liệu mục tiêu hay danh sách cho trước>

{{
  "entities": [
    {{"text": "span text chính xác từ câu gốc", "type": "loại thực thể"}}
  ]
}}
"""

EVENTS_BUILDER_SYSTEM_PROMPT_TEMPLATE = """Bạn là một trợ lý AI tạo dữ liệu huấn luyện (dataset builder) nhận dạng sự kiện cho tiếng Việt.
Nhiệm vụ của bạn là viết một quá trình suy luận từng bước tự nhiên giải thích lý do trích xuất các trigger (từ hoặc cụm từ biểu thị sự kiện) cụ thể từ câu tiếng Việt, sau đó trả về kết quả JSON chứa các trigger này.

Bạn sẽ được cung cấp:
1. Một câu tiếng Việt.
2. Danh sách các trigger sự kiện mục tiêu cần phải trích xuất (đây là nhãn đúng).

## CÁC LOẠI SỰ KIỆN:
{event_types_text}

## QUY TẮC BẮT BUỘC KHI SINH SUY LUẬN:
1. TRONG BÀI VIẾT SUY LUẬN, TUYỆT ĐỐI KHÔNG ĐƯỢC ĐẢ ĐỘNG đến các từ ngữ và khái niệm liên quan đến việc có dữ liệu cho trước, ví dụ: "GOLD", "mục tiêu", "cho trước", "yêu cầu", "nhãn", "trùng khớp", "danh sách", v.v. Hãy viết như thể bạn tự phân tích câu và tự phát hiện ra chúng từ đầu.
2. Hãy viết suy luận dưới góc nhìn của một mô hình đang tự mình phân tích và trích xuất trigger từ câu gốc một cách tự nhiên từ đầu:
    - Bước 1: Xác định toàn bộ các trigger ứng viên biểu thị hành động/sự kiện có trong câu.
    - Bước 2: Phân tích ngữ cảnh và định nghĩa loại sự kiện để giải thích vì sao loại sự kiện đó là phù hợp nhất cho từng trigger.
    - Bước 3: Đưa ra định dạng JSON kết quả chứa các trigger này.
3. Phần JSON kết quả phải khớp hoàn toàn với danh sách trigger mục tiêu được cung cấp.

## ĐỊNH DẠNG ĐẦU RA (Không thêm bất kỳ từ ngữ nào ngoài định dạng này):
[QUÁ TRÌNH SUY LUẬN TỪNG BƯỚC]

<tiến trình suy luận tự nhiên, không nhắc đến việc có dữ liệu mục tiêu hay danh sách cho trước>

{{
  "events": [
    {{"trigger": "span text trigger chính xác từ câu gốc", "type": "loại sự kiện"}}
  ]
}}
"""

EVENT_ARGUMENTS_BUILDER_SYSTEM_PROMPT_TEMPLATE = """Bạn là một trợ lý AI tạo dữ liệu huấn luyện (dataset builder) gán vai trò thực thể trong sự kiện cho tiếng Việt.
Nhiệm vụ của bạn: cho trước một câu, loại sự kiện, trigger, danh sách thực thể ứng viên, danh sách loại tham số hợp lệ, và danh sách đối số mục tiêu.
Hãy viết một quá trình suy luận từng bước tự nhiên giải thích tại sao các thực thể ứng viên lại đóng vai trò tương ứng trong sự kiện, sau đó trả về kết quả JSON chứa các đối số này.

## QUY TẮC BẮT BUỘC KHI SINH SUY LUẬN:
1. TRONG BÀI VIẾT SUY LUẬN, TUYỆT ĐỐI KHÔNG ĐƯỢC ĐẢ ĐỘNG đến các từ ngữ và khái niệm liên quan đến việc có dữ liệu cho trước, ví dụ: "GOLD", "mục tiêu", "cho trước", "yêu cầu", "nhãn", "trùng khớp", "danh sách", v.v. Hãy viết như thể bạn tự phân tích câu và tự phát hiện ra chúng từ đầu.
2. Hãy viết suy luận dưới góc nhìn của một mô hình đang tự mình phân tích và gán tham số từ câu gốc một cách tự nhiên từ đầu:
    - Bước 1: Xác định các thực thể ứng viên liên quan tới sự kiện thông qua mối quan hệ với trigger.
    - Bước 2: Phân tích ngữ cảnh để giải thích vì sao từng loại tham số được gán là phù hợp nhất cho thực thể tương ứng.
    - Bước 3: Đưa ra định dạng JSON kết quả chứa các đối số này.
3. Phần JSON kết quả phải khớp hoàn toàn với danh sách đối số mục tiêu được cung cấp.

## ĐỊNH DẠNG ĐẦU RA (Không thêm bất kỳ từ ngữ nào ngoài định dạng này):
[QUÁ TRÌNH SUY LUẬN TỪNG BƯỚC]

<tiến trình suy luận tự nhiên, không nhắc đến việc có dữ liệu mục tiêu hay danh sách cho trước>

{
  "arguments": [
    {"text": "văn bản chính xác khớp với thực thể ứng viên", "type": "loại chính xác từ danh sách hợp lệ"}
  ]
}
"""

FULL_BUILDER_SYSTEM_PROMPT_TEMPLATE = """Bạn là một trợ lý AI tạo dữ liệu huấn luyện (dataset builder) trích xuất thực thể, sự kiện và đối số cho tiếng Việt.
Nhiệm vụ của bạn là viết một quá trình suy luận từng bước tự nhiên giải thích lý do trích xuất thực thể, trigger sự kiện và các đối số từ câu tiếng Việt, sau đó trả về kết quả JSON chứa thông tin này.

Bạn sẽ được cung cấp:
1. Một câu tiếng Việt.
2. Danh sách thực thể mục tiêu và sự kiện mục tiêu (kèm đối số) cần phải trích xuất (đây là nhãn đúng).

## CÁC LOẠI THỰC THỂ:
{entity_types_text}

## CÁC LOẠI SỰ KIỆN:
{event_types_text}

## CÁC LOẠI THAM SỐ:
{argument_types_text}

## QUY TẮC BẮT BUỘC KHI SINH SUY LUẬN:
1. TRONG BÀI VIẾT SUY LUẬN, TUYỆT ĐỐI KHÔNG ĐƯỢC ĐẢ ĐỘNG đến các từ ngữ và khái niệm liên quan đến việc có dữ liệu cho trước, ví dụ: "GOLD", "mục tiêu", "cho trước", "yêu cầu", "nhãn", "trùng khớp", "danh sách", v.v. Hãy viết như thể bạn tự phân tích câu và tự phát hiện ra chúng từ đầu.
2. Hãy viết suy luận dưới góc nhìn của một mô hình đang tự mình phân tích và trích xuất từ câu gốc một cách tự nhiên từ đầu:
    - Bước 1: Xác định tất cả các thực thể có trong câu và giải thích lý do gán loại của chúng.
    - Bước 2: Xác định tất cả các trigger sự kiện có trong câu và giải thích lý do gán loại của chúng.
    - Bước 3: Đối với mỗi trigger sự kiện, giải thích vì sao các đối số tương ứng lại được chọn và gán loại tham số đó.
    - Bước 4: Kết luận và đưa kết quả JSON.
3. Phần JSON kết quả phải khớp hoàn toàn với danh sách thực thể và sự kiện mục tiêu được cung cấp.

## ĐỊNH DẠNG ĐẦU RA (Không thêm bất kỳ từ ngữ nào ngoài định dạng này):
[QUÁ TRÌNH SUY LUẬN TỪNG BƯỚC]

<tiến trình suy luận tự nhiên, không nhắc đến việc có dữ liệu mục tiêu hay danh sách cho trước>

{{
  "entities": [
    {{"text": "văn bản thực thể chính xác", "type": "entity_type"}}
  ],
  "events": [
    {{
      "type": "event_type",
      "trigger": "văn bản trigger chính xác",
      "arguments": [
        {{"text": "văn bản thực thể chính xác", "type": "argument_type"}}
      ]
    }}
  ]
}}
"""


FINETUNED_ENTITIES_SYSTEM_PROMPT = "Trích xuất các đề cập thực thể từ câu tiếng Việt đã cho. Hãy suy nghĩ theo từng bước."

FINETUNED_EVENTS_SYSTEM_PROMPT = "Trích xuất các trigger (từ hoặc cụm từ biểu thị sự kiện) từ câu tiếng Việt đã cho. Hãy suy nghĩ theo từng bước."

FINETUNED_ARGUMENTS_SYSTEM_PROMPT = "Gán nhãn loại tham số sự kiện cho các thực thể phù hợp từ danh sách thực thể ứng viên đã cho. Hãy suy nghĩ theo từng bước."

FINETUNED_FULL_SYSTEM_PROMPT = "Trích xuất thực thể kèm span text, trigger sự kiện và tham số tương ứng của từng thực thể từ câu tiếng Việt đã cho. Hãy suy nghĩ theo từng bước."