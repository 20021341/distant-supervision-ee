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

## ĐỊNH DẠNG ĐẦU RA:
[QUÁ TRÌNH SUY LUẬN TỪNG BƯỚC]

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

ENTITIES_FEW_SHOT_EXAMPLES = """
--- Ví dụ 1 ---
Câu: "Khi đi vào xã Cổ Đông , do trời mưa Hoài bị ngã nên cởi giày và áo bẩn vứt đi ; chân chảy máu vì giẫm vào thuỷ tinh ."

Bước 1: Xác định các thực thể ứng viên trong câu.
Câu văn mô tả sự việc: khi đi vào một địa danh hành chính, nhân vật Hoài bị ngã do trời mưa, phải cởi giày và áo bẩn vứt đi, chân bị chảy máu vì giẫm vào thủy tinh. Các cụm từ đáng chú ý gồm: "xã Cổ Đông" (địa danh), "Hoài" (tên người), ngoài ra còn có "trời mưa" (hiện tượng thời tiết), "giày", "áo" (đồ dùng cá nhân), "thuỷ tinh" (vật liệu thường).

Bước 2: Phân tích ngữ cảnh và phân loại từng thực thể.
- "xã Cổ Đông": Đây là tên một đơn vị hành chính cấp xã — một khu vực địa lý gắn liền với chính quyền quản lý. Theo định nghĩa, đơn vị hành chính như xã, huyện, tỉnh đều thuộc loại Geopolitical-Entity, nên đây là thực thể Geopolitical-Entity chứ không phải Location thông thường.
- "Hoài": Đây là tên riêng của một cá nhân xuất hiện trong câu với vai trò chủ thể của hành động (bị ngã, cởi giày, chân chảy máu). Do đó đây là thực thể Person.
- Các yếu tố khác không đủ điều kiện: "trời mưa" chỉ là hiện tượng thời tiết, không phải mốc thời gian; "giày", "áo" là đồ vật cá nhân; "thuỷ tinh" là mảnh kính vỡ vô tình trên đường, không phải vũ khí được sử dụng có chủ đích; câu cũng không nhắc đến tổ chức, phương tiện, tiền bạc hay con số nào.

Bước 3: Kết luận.
Từ phân tích trên, hai thực thể cần trích xuất là "xã Cổ Đông" (Geopolitical-Entity) và "Hoài" (Person).

{
  "entities": [
    {"text": "xã Cổ Đông", "type": "Geopolitical-Entity"},
    {"text": "Hoài", "type": "Person"}
  ]
}

--- Ví dụ 2 ---
Câu: "Tuy nhiên , sau khi ông Pol tuyên bố rút lại dự thảo , cuộc biểu tình dự kiến diễn ra hôm nay cũng được huỷ bỏ ."

Bước 1: Đọc và phân tích câu. Câu này kể về việc sau khi có tuyên bố rút lại dự thảo, cuộc biểu tình vốn được lên kế hoạch đã bị huỷ bỏ. Yếu tố đáng chú ý nhất để trích xuất ở đây là mốc thời gian gắn liền với sự kiện biểu tình.

Bước 2: Phân tích ngữ cảnh của từng thành phần trong câu:
- Cụm từ "hôm nay" xuất hiện trong cấu trúc "dự kiến diễn ra hôm nay", dùng để chỉ ngày mà cuộc biểu tình được dự kiến tổ chức. Đây là một biểu thức thời gian tương đối, tính từ thời điểm phát ngôn, nên rõ ràng thuộc loại thực thể Time.
- Các danh từ còn lại như "dự thảo", "cuộc biểu tình" là những khái niệm chỉ văn bản và sự kiện chung chung, không rơi vào bất kỳ loại thực thể nào đã định nghĩa.

Bước 3: Kết luận, thực thể duy nhất cần trích xuất từ câu này là cụm thời gian "hôm nay" với loại Time.

{
  "entities": [
    {"text": "hôm nay", "type": "Time"}
  ]
}

--- Ví dụ 3 ---
Câu: "Ngân hàng cổ phần Bưu điện Liên Việt cũng báo cáo bằng văn bản với toà án đã khởi kiện Công ty PVC Land ."

Bước 1: Đọc và xác định các thực thể ứng viên trong câu.
Câu văn mô tả việc "Ngân hàng cổ phần Bưu điện Liên Việt" báo cáo bằng văn bản với toà án về việc đã khởi kiện "Công ty PVC Land". Các cụm từ đáng chú ý trong câu gồm: "Ngân hàng cổ phần Bưu điện Liên Việt", "toà án" và "Công ty PVC Land".

Bước 2: Phân tích ngữ cảnh và phân loại từng thực thể.
- "Ngân hàng cổ phần Bưu điện Liên Việt": đây là tên gọi đầy đủ của một ngân hàng thương mại cổ phần, thuộc nhóm tổ chức tài chính. Ngân hàng là một loại hình tổ chức chính thức, vì vậy cụm từ này được phân loại là Organization.
- "Công ty PVC Land": đây là tên riêng của một doanh nghiệp, là bên bị khởi kiện trong câu. Công ty cũng là một tổ chức chính thức, vì vậy cụm từ này được phân loại là Organization.
- "toà án" trong câu chỉ được dùng như một cách gọi chung, mang chức năng ngữ pháp chỉ nơi tiếp nhận báo cáo và đơn kiện, không phải tên gọi cụ thể của một cơ quan được nhắc đến như một thực thể riêng, nên không đưa vào kết quả trích xuất.

Bước 3: Tổng hợp kết quả.
Câu chứa hai thực thể Organization: ngân hàng khởi kiện và công ty bị khởi kiện.

{
  "entities": [
    {"text": "Ngân hàng cổ phần Bưu điện Liên Việt", "type": "Organization"},
    {"text": "Công ty PVC Land", "type": "Organization"}
  ]
}

--- Ví dụ 4 ---
Câu: "Ngày 30/3 , công an thành phố Vinh khởi tố bị can với Nghĩa về tội Làm nhục người khác , theo điều 155 Bộ luật hình sự ."

Bước 1: Xác định các thực thể ứng viên trong câu.

Câu: "Ngày 30/3 , công an thành phố Vinh khởi tố bị can với Nghĩa về tội Làm nhục người khác , theo điều 155 Bộ luật hình sự ."

Quan sát câu, tôi nhận thấy có các thành phần tiềm năng sau:
- "Ngày 30/3": một mốc thời gian cụ thể mở đầu câu.
- "công an thành phố Vinh": một cơ quan chức năng thực hiện hành động "khởi tố".
- "bị can với Nghĩa": tham chiếu đến cá nhân bị khởi tố, trong đó "Nghĩa" là tên riêng của người này.
- "Làm nhục người khác": tên gọi của tội danh được nêu ra.
- "điều 155 Bộ luật hình sự": trích dẫn văn bản pháp luật làm căn cứ.

Bước 2: Phân tích ngữ cảnh và xác định loại thực thể phù hợp.

- "Ngày 30/3" là biểu thức chỉ ngày tháng cụ thể, đánh dấu thời điểm xảy ra sự kiện khởi tố → thuộc loại Time.
- "công an thành phố Vinh" là cơ quan công an cấp thành phố, một cơ quan nhà nước chính thức thực hiện hoạt động tố tụng → thuộc loại Organization.
- "Nghĩa" là tên riêng của cá nhân bị khởi tố trong câu; dù câu có dùng từ "bị can" để chỉ vai trò, nhưng tên riêng "Nghĩa" mới là cách gọi trực tiếp và cụ thể nhất cho người tham gia sự kiện → thuộc loại Person.
- "Làm nhục người khác" là tội danh được nêu rõ trong câu ("về tội Làm nhục người khác"), mô tả hành vi vi phạm pháp luật mà bị can bị cáo buộc → thuộc loại Crime.
- Riêng "điều 155 Bộ luật hình sự" là dẫn chiếu đến điều luật/căn cứ pháp lý chứ không phải hành vi phạm tội hay mức án tuyên, nên không đưa vào kết quả.

Bước 3: Tổng hợp kết quả JSON.

{
  "entities": [
    {"text": "Nghĩa", "type": "Person"},
    {"text": "công an thành phố Vinh", "type": "Organization"},
    {"text": "Ngày 30/3", "type": "Time"},
    {"text": "Làm nhục người khác", "type": "Crime"}
  ]
}

--- Ví dụ 5 ---
Câu: "Hôm 20/2 HĐXX mở phiên xử công khai , hai bên tranh cãi căng thẳng về quan hệ hôn nhân , nuôi dưỡng con cái , phân chia tài sản và điều hành Trung Nguyên ."

Bước 1: Đọc và xác định các thực thể ứng viên trong câu.

Câu: "Hôm 20/2 HĐXX mở phiên xử công khai , hai bên tranh cãi căng thẳng về quan hệ hôn nhân , nuôi dưỡng con cái , phân chia tài sản và điều hành Trung Nguyên ."

Khi phân tích câu, tôi nhận thấy câu này mô tả một phiên tòa xét xử công khai với các nội dung tranh chấp. Các yếu tố đáng chú ý trong câu:
- "Hôm 20/2": cụm từ chỉ thời điểm diễn ra sự kiện.
- "HĐXX": chủ thể mở phiên xử.
- "hai bên": các bên tranh cãi.
- "Trung Nguyên": đối tượng được điều hành.

Bước 2: Phân tích ngữ cảnh và xác định loại thực thể phù hợp.

- "20/2" là một mốc ngày tháng cụ thể (ngày 20 tháng 2), đứng sau từ "Hôm" để chỉ thời điểm phiên xử diễn ra. Theo định nghĩa loại Time (mốc thời gian, ngày tháng, giờ giấc), đây là một biểu thức thời gian rõ ràng và cần được trích xuất. Cụm "Hôm" là từ chỉ thị thời gian tương đối đi kèm, còn phần mốc ngày cụ thể chính là "20/2".

- Các thành phần còn lại trong câu ("HĐXX", "hai bên", "Trung Nguyên") đóng vai trò chủ ngữ, đối tượng tranh chấp trong ngữ cảnh phiên tòa, không phải là mốc thời gian, giá trị tiền tệ, con số hay hành vi phạm tội được nêu đích danh trong câu này.

Bước 3: Kết luận.

Thực thể duy nhất cần trích xuất từ câu là mốc thời gian "20/2" với loại Time.

{
  "entities": [
    {"text": "20/2", "type": "Time"}
  ]
}
"""

EVENTS_FEW_SHOT_EXAMPLES = """
--- Ví dụ 1 ---
Câu: "Tuyên bố này cho thấy các cố vấn quân sự hàng đầu của Tổng thống đã thành công trong việc thuyết phục ông không vội vàng rút quân khỏi Syria ."

Bước 1: Xác định các trigger ứng viên trong câu.
- Câu: "Tuyên bố này cho thấy các cố vấn quân sự hàng đầu của Tổng thống đã thành công trong việc thuyết phục ông không vội vàng rút quân khỏi Syria."
- Các từ/cụm từ có khả năng biểu thị sự kiện: "tuyên bố", "cho thấy", "thuyết phục", "rút".
- Trong đó, "rút" xuất hiện trong cụm "rút quân khỏi Syria" và là động từ hành động chính đáng chú ý nhất.

Bước 2: Phân tích ngữ cảnh và loại sự kiện cho từng ứng viên.
- "tuyên bố": chỉ hành động phát ngôn/khẳng định của một bên, không thuộc bất kỳ loại sự kiện nào trong hệ thống phân loại hiện có.
- "cho thấy": chỉ quan hệ diễn giải giữa phát ngôn và nội dung, không phải sự kiện thực thể.
- "thuyết phục": là hành động tác động tinh thần/thuyết phục, không nằm trong danh mục loại sự kiện được định nghĩa.
- "rút": trong cụm "rút quân khỏi Syria", động từ này biểu thị việc rút lui lực lượng quân sự khỏi một khu vực địa lý. Đây chính là sự di chuyển của người/vũ khí/phương tiện từ nơi này sang nơi khác, mang tính chiến thuật/quân sự — hoàn toàn phù hợp với định nghĩa của Movement:Transport. Mặc dù câu nói theo hướng phủ định ("không vội vàng rút"), bản thân động từ "rút" vẫn là trigger biểu thị loại sự kiện di chuyển này.

Bước 3: Kết luận.
- Trigger duy nhất cần trích xuất là "rút" với loại sự kiện Movement:Transport.

{
  "events": [
    {"trigger": "rút", "type": "Movement:Transport"}
  ]
}

--- Ví dụ 2 ---
Câu: "Ông Hưng nổ nhiều phát súng tại quán ăn đêm ."

Bước 1: Xác định các trigger ứng viên trong câu.
Câu "Ông Hưng nổ nhiều phát súng tại quán ăn đêm." mô tả một hành động được thực hiện bởi chủ thể "Ông Hưng". Cụm từ trung tâm biểu thị hành động ở đây là "nổ nhiều phát súng" — đây là cụm động từ chỉ việc xả/nổ súng liên tiếp, một hành vi bạo lực rõ ràng. Ngoài ra, không có cụm từ nào khác trong câu mang tính sự kiện (như sinh ra, kết hôn, bắt giữ...), nên "nổ nhiều phát súng" là trigger ứng viên duy nhất đáng chú ý.

Bước 2: Phân tích ngữ cảnh và xác định loại sự kiện.
- Chủ thể: "Ông Hưng" — người thực hiện hành vi.
- Hành động: "nổ nhiều phát súng" — việc sử dụng vũ khí (súng) để bắn, đây là hành vi tấn công vũ trang nhằm gây hại hoặc đe dọa.
- Bối cảnh: "tại quán ăn đêm" — địa điểm công cộng nơi hành vi diễn ra.
Theo định nghĩa của Conflict:Attack (hành vi bạo lực vật lý, tấn công vũ trang nhằm gây hại cho chủ thể khác), việc nổ súng tại một địa điểm công cộng hoàn toàn phù hợp với loại sự kiện này. Lưu ý theo quy tắc, khi cụm từ chứa cả hành động và vũ khí ("nổ súng"), ta trích xuất toàn bộ cụm hành động "nổ nhiều phát súng" làm trigger thay vì tách riêng danh từ "súng".

Bước 3: Kết luận.
Trigger duy nhất cần trích xuất là "nổ nhiều phát súng" với loại sự kiện Conflict:Attack.

{
  "events": [
    {"trigger": "nổ nhiều phát súng", "type": "Conflict:Attack"}
  ]
}

--- Ví dụ 3 ---
Câu: "Dẫn kinh nghiệm các nước , ông cho hay , họ thừa nhận việc dùng tiền thuế đóng góp của dân vào giải cứu ngân hàng , nhưng có phương án phục hồi rõ ràng và “ giám sát chặt chẽ từng đồng đôla gói giải cứu đó ” ."

Bước 1: Xác định các trigger ứng viên trong câu.

Câu nói về việc sử dụng tiền thuế của dân để giải cứu ngân hàng. Các cụm từ tiềm năng biểu thị sự kiện bao gồm: "dùng tiền thuế", "đóng góp", "giải cứu".

Bước 2: Phân tích ngữ cảnh cho từng ứng viên.

- "dùng tiền thuế": Đây là hành động sử dụng tiền, không phải hành động chuyển giao tiền giữa các bên một cách trực tiếp, nên không phải là trigger của sự kiện chuyển tiền.
- "giải cứu": Cụm từ này xuất hiện hai lần ("giải cứu ngân hàng", "gói giải cứu"), mang nghĩa hành động cứu trợ tài chính, nhưng bản chất là mục đích của việc sử dụng tiền chứ không phải động từ biểu thị dòng tiền dịch chuyển giữa các chủ thể.
- "đóng góp": Trong cụm "tiền thuế đóng góp của dân", từ "đóng góp" biểu thị rõ ràng hành động người dân nộp/đóng tiền (thông qua thuế) vào quỹ chung — tức dòng tiền dịch chuyển từ cá nhân người dân sang phía nhà nước/quỹ giải cứu. Đây chính là hành vi chuyển tiền giữa các bên, phù hợp với định nghĩa Transaction:Transfer-Money (bất kỳ hành động nào khiến dòng tiền dịch chuyển từ chủ thể này sang chủ thể khác).

Như vậy, trigger duy nhất thỏa mãn là "đóng góp" với loại sự kiện Transaction:Transfer-Money.

Bước 3: Kết quả cuối cùng.

{
  "events": [
    {"trigger": "đóng góp", "type": "Transaction:Transfer-Money"}
  ]
}

--- Ví dụ 4 ---
Câu: "Ít nhất 10 người đã thiệt mạng và hàng chục người nhập viện trong các vụ bạo lực ở Thái Lan ."

Bước 1: Xác định các trigger ứng viên trong câu.
Câu văn mô tả hậu quả của một loạt sự kiện bạo lực tại Thái Lan. Tôi đọc kỹ câu và phát hiện ba cụm từ mang tính sự kiện rõ rệt:
- "thiệt mạng": biểu thị việc con người tử vong ("Ít nhất 10 người đã thiệt mạng").
- "nhập viện": biểu thị việc hàng chục người bị thương phải vào bệnh viện điều trị.
- "bạo lực": danh từ chỉ các vụ việc bạo động xảy ra ở Thái Lan.

Bước 2: Phân tích ngữ cảnh và gán loại sự kiện cho từng trigger.
- Với "thiệt mạng": Đây là từ ngữ trang trọng thường dùng trong báo chí để chỉ cái chết của con người do tai nạn, thiên tai hoặc bạo lực. Ngữ cảnh "Ít nhất 10 người đã thiệt mạng" khẳng định rõ số người tử vong, hoàn toàn phù hợp với định nghĩa Life:Die.
- Với "nhập viện": Cụm từ này mô tả việc người dân phải vào viện cấp cứu/điều trị, hàm ý họ đã chịu thương tích vật lý trong các vụ việc được nhắc đến. Theo quy ước, hành động nhập viện cấp cứu là dấu hiệu của việc bị thương, nên đây là trigger của Life:Injure.
- Với "bạo lực": Trong ngữ cảnh "các vụ bạo lực ở Thái Lan", cụm từ này không chỉ đơn thuần là hành vi tấn công cá nhân mà chỉ các vụ bất ổn, bạo động công cộng diễn ra trên diện rộng — đặc trưng của các cuộc biểu tình/tụ tập phản đối biến thành bạo loạn. Do đó loại sự kiện phù hợp nhất là Conflict:Demonstrate.

Bước 3: Tổng hợp kết quả.
Ba trigger đã được xác nhận: "thiệt mạng" (Life:Die), "nhập viện" (Life:Injure) và "bạo lực" (Conflict:Demonstrate). Tôi trả về kết quả dưới dạng JSON:

{
  "events": [
    {"trigger": "thiệt mạng", "type": "Life:Die"},
    {"trigger": "nhập viện", "type": "Life:Injure"},
    {"trigger": "bạo lực", "type": "Conflict:Demonstrate"}
  ]
}

--- Ví dụ 5 ---
Câu: "Liên minh đối lập Islami Jamhoori Ittehad ( IJT ) chiến thắng cuộc bầu cử cuối năm đó và lên cầm quyền ."

Bước 1: Xác định các trigger ứng viên trong câu.
Câu nói về liên minh đối lập Islami Jamhoori Ittehad (IJT) giành chiến thắng trong một sự kiện chính trị cuối năm và nắm quyền lực. Các cụm từ ứng viên biểu thị sự kiện gồm:
- "chiến thắng": diễn tả việc đạt được thắng lợi trong một cuộc cạnh tranh.
- "bầu cử": chỉ quá trình bỏ phiếu để chọn người/đảng vào vị trí quyền lực.
- "lên cầm quyền": diễn tả việc bắt đầu nắm giữ quyền lực sau khi giành được vị trí.

Bước 2: Phân tích ngữ cảnh và xác định loại sự kiện phù hợp.
- "chiến thắng" ở đây là kết quả của quá trình bầu cử, mang tính mô tả chung về thắng lợi chứ không phải hành động bầu chọn hay trúng cử trực tiếp theo nghĩa pháp lý của sự kiện bầu cử.
- "bầu cử" là từ khóa trung tâm: toàn bộ câu xoay quanh việc liên minh này "chiến thắng cuộc bầu cử", tức là họ đã được cử tri bỏ phiếu bầu chọn để giành vị trí cầm quyền. Theo định nghĩa, sự kiện Personnel:Elect bao gồm việc một chủ thể chính thức được bầu chọn vào một vị trí thông qua bỏ phiếu. Do đó "bầu cử" chính là trigger thể hiện trực tiếp sự kiện bầu cử này.
- "lên cầm quyền" chỉ mô tả hệ quả là việc nắm quyền sau khi trúng cử, không phải hành động bầu chọn, nên không được trích xuất như một trigger riêng cho sự kiện Elect.

Kết luận: Trigger duy nhất cần trích xuất là "bầu cử" với loại sự kiện Personnel:Elect.

{
  "events": [
    {"trigger": "bầu cử", "type": "Personnel:Elect"}
  ]
}
"""

EVENT_ARGUMENTS_FEW_SHOT_EXAMPLES = """
--- Ví dụ 1 ---
Câu: "Ít nhất 10 người đã thiệt mạng và hàng chục người nhập viện trong các vụ bạo lực ở Thái Lan ."
Loại sự kiện: "Conflict:Demonstrate"
Trigger: "bạo lực"

Trong câu văn "Ít nhất 10 người đã thiệt mạng và hàng chục người nhập viện trong các vụ bạo lực ở Thái Lan .", từ khóa "bạo lực" đóng vai trò là trigger chỉ một sự kiện xung đột/biểu tình đang diễn ra.

Khi xem xét các thực thể trong câu:
- "10 người" và "hàng chục người" là những đối tượng chịu tác động hoặc tham gia vào sự việc, nhưng xét về mặt không gian xảy ra hành vi bạo lực, họ là nạn nhân hoặc người liên quan trực tiếp chứ không phải là địa điểm.
- "Thái Lan" được nhắc đến sau giới từ "ở", xác định phạm vi không gian nơi các vụ bạo lực này diễn ra. Do đó, "Thái Lan" đóng vai trò là địa điểm (Place) của sự kiện.

Vì vậy, thực thể "Thái Lan" được gán loại tham số là "Place".

{
  "arguments": [
    {"text": "Thái Lan", "type": "Place"}
  ]
}

--- Ví dụ 2 ---
Câu: "Tuyên bố này cho thấy các cố vấn quân sự hàng đầu của Tổng thống đã thành công trong việc thuyết phục ông không vội vàng rút quân khỏi Syria ."
Loại sự kiện: "Movement:Transport"
Trigger: "rút"

Trong câu văn "Tuyên bố này cho thấy các cố vấn quân sự hàng đầu của Tổng thống đã thành công trong việc thuyết phục ông không vội vàng rút quân khỏi Syria.", sự kiện di chuyển được kích hoạt bởi từ "rút".

Phân tích các thực thể ứng viên:
- Thực thể "ông" được nhắc đến trong ngữ cảnh là người đưa ra quyết định về việc rút quân. Tuy nhiên, xét theo hành động "rút quân", người thực hiện hành động di chuyển (Agent) chính là chủ thể được nhắc đến qua đại từ này. Do đó, "ông" đóng vai trò là Agent (người thực hiện việc rút).
- Thực thể "quân" trong cụm từ "rút quân" chỉ đối tượng (lực lượng quân đội) bị di chuyển hoặc thay đổi vị trí địa lý. Trong loại sự kiện vận chuyển, đối tượng được di dời này tương ứng với vai trò Artifact.
- Thực thể "Syria" là địa danh đi kèm với giới từ "khỏi", chỉ nơi mà lực lượng quân đội đang hiện diện và sẽ rời đi. Do đó, "Syria" đóng vai trò là Origin (điểm xuất phát/nơi bắt đầu sự di chuyển).

Kết luận các vai trò:
- "ông" -> Agent
- "quân" -> Artifact
- "Syria" -> Origin

{
  "arguments": [
    {"text": "ông", "type": "Agent"},
    {"text": "Syria", "type": "Origin"},
    {"text": "quân", "type": "Artifact"}
  ]
}

--- Ví dụ 3 ---
Câu: "Chiều 1/5 , Phong mang theo nhiều dây chuyền , nhẫn vàng đến một tiệm vàng S. nằm trên địa bàn thị xã Ayun Pa để bán thì bị chủ tiệm nghi ngờ là tài sản trộm cắp nên báo với lực lượng công an ."
Loại sự kiện: "Transaction:Transfer-Money"
Trigger: "mang"

Trong câu văn trên, hành động "mang" (trong ngữ cảnh mang tài sản đến để bán) đóng vai trò là trigger cho một sự kiện giao dịch/chuyển nhượng tài sản.

- Đầu tiên, xét thực thể "Phong", đây là người trực tiếp thực hiện hành vi mang các vật phẩm đến tiệm vàng để giao dịch. Do đó, "Phong" đóng vai trò là người thực hiện việc chuyển giao tài sản (Giver).
- Tiếp theo, xét cụm từ "nhiều dây chuyền , nhẫn vàng", đây là các vật phẩm có giá trị tương đương với tiền tệ được đưa vào giao dịch. Trong ngữ cảnh của sự kiện chuyển nhượng tài chính này, cụm từ này đóng vai trò là đối tượng giá trị được chuyển đi (Money).
- Các thực thể khác như "một tiệm vàng S." hay địa danh "thị xã Ayun Pa" là các yếu tố về địa điểm, không thuộc vào các tham số cốt lõi của giao dịch được xác định trong trường hợp này.

{
  "arguments": [
    {"text": "Phong", "type": "Giver"},
    {"text": "nhiều dây chuyền , nhẫn vàng", "type": "Money"}
  ]
}

--- Ví dụ 4 ---
Câu: "Chiều 1/5 , Phong mang theo nhiều dây chuyền , nhẫn vàng đến một tiệm vàng S. nằm trên địa bàn thị xã Ayun Pa để bán thì bị chủ tiệm nghi ngờ là tài sản trộm cắp nên báo với lực lượng công an ."
Loại sự kiện: "Movement:Transport"
Trigger: "đến"

Trong câu văn "Chiều 1/5 , Phong mang theo nhiều dây chuyền , nhẫn vàng đến một tiệm vàng S. nằm trên địa bàn thị xã Ayun Pa để bán thì bị chủ tiệm nghi ngờ là tài sản trộm cắp nên báo với lực lượng công an .", sự kiện di chuyển được kích hoạt bởi từ "đến".

- Đầu tiên, xét thực thể "Phong": Đây là người thực hiện hành động di chuyển (mang theo đồ vật đến một địa điểm), do đó "Phong" đóng vai trò là chủ thể thực hiện hành động, tương ứng với tham số Agent.
- Tiếp theo, xét cụm từ "một tiệm vàng S.": Đây là địa điểm mà nhân vật Phong hướng tới để thực hiện việc bán vàng, đóng vai trò là đích đến của hành trình di chuyển, tương ứng với tham số Destination.
- Cuối cùng, xét cụm "nằm trên địa bàn thị xã Ayun Pa": Cụm từ này mô tả vị trí địa lý của tiệm vàng S., xác định rõ hơn về điểm đến trong không gian, do đó nó cũng đóng vai trò là một phần của thông tin đích đến (Destination).

{
  "arguments": [
    {"text": "Phong", "type": "Agent"},
    {"text": "một tiệm vàng S.", "type": "Destination"},
    {"text": "nằm trên địa bàn thị xã Ayun Pa", "type": "Destination"}
  ]
}

--- Ví dụ 5 ---
Câu: "Khi đi vào xã Cổ Đông , do trời mưa Hoài bị ngã nên cởi giày và áo bẩn vứt đi ; chân chảy máu vì giẫm vào thuỷ tinh ."
Loại sự kiện: "Movement:Transport"
Trigger: "đi vào"

- Bước 1: Phân tích câu văn, ta thấy cụm từ "đi vào" đóng vai trò là trigger (tác nhân kích hoạt) cho một sự kiện di chuyển/vận chuyển. Các thực thể liên quan trực tiếp đến hành động này trong câu là "xã Cổ Đông" và "Hoài".
- Bước 2: Xem xét vai trò của từng thực thể đối với hành động "đi vào":
    - "Hoài" là người thực hiện hành động di chuyển, chủ thể thực hiện việc đi vào một địa điểm. Do đó, "Hoài" đóng vai trò là Agent (Chủ thể).
    - "xã Cổ Đông" là địa danh được nhắc đến sau cụm từ "đi vào", đóng vai trò là nơi mà chủ thể hướng tới hoặc kết thúc hành trình di chuyển trong ngữ cảnh này. Do đó, "xã Cổ Đông" đóng vai trò là Destination (Điểm đến).
- Bước 3: Tổng hợp lại, ta có hai đối số tương ứng với sự kiện di chuyển là Agent là "Hoài" và Destination là "xã Cổ Đông".

{
  "arguments": [
    {"text": "xã Cổ Đông", "type": "Destination"},
    {"text": "Hoài", "type": "Agent"}
  ]
}
"""

FULL_FEW_SHOT_EXAMPLES = """
--- Ví dụ 1 ---
Câu: "Bộ Ngoại giao Pakistan cho biết Varthaman được đối xử phù hợp với luật pháp quốc tế và việc phóng thích anh này " nhằm giảm căng thẳng gia tăng với Ấn Độ " ."

- Bước 1: Phân tích các thực thể trong câu.
    - "Bộ Ngoại giao Pakistan": Đây là một cơ quan nhà nước, thuộc loại Organization.
    - "Varthaman": Tên riêng của một cá nhân, thuộc loại Person.
    - "Ấn Độ": Tên một quốc gia, thuộc loại Geopolitical-Entity.
    - "anh này": Đại từ nhân xưng chỉ Varthaman, thuộc loại Person. Trong ngữ cảnh câu, "anh" được dùng để chỉ đối tượng cụ thể đang được nhắc đến.

- Bước 2: Xác định các sự kiện.
    - Cụm từ "phóng thích" chỉ hành động cho phép một người được tự do, thoát khỏi sự giam giữ hoặc quản lý của pháp luật/cơ quan chức năng. Điều này tương ứng với loại sự kiện Justice:Release-Parole.

- Bước 3: Xác định các đối số cho sự kiện.
    - Với trigger "phóng thích", đối tượng được giải phóng là "anh này" (đại diện cho Varthaman). Do đó, "anh" được xác định là đối số thuộc loại Person (người được thả).

- Bước 4: Kết luận và trích xuất kết quả.
    - Thực thể mục tiêu là "anh" (Person).
    - Sự kiện là "phóng thích" (Justice:Release-Parole) với đối số là "anh" (Person).

{
  "entities": [
    {"text": "anh", "type": "Person"}
  ],
  "events": [
    {
      "type": "Justice:Release-Parole",
      "trigger": "phóng thích",
      "arguments": [
        {"text": "anh", "type": "Person"}
      ]
    }
  ]
}

--- Ví dụ 2 ---
Câu: "Một cán bộ trại giam cho biết , những ngày bị biệt giam trong tù sau phiên phúc thẩm , Nghĩa có những biểu hiện tâm lý khó nắm bắt ."

- Bước 1: Phân tích các thực thể trong câu.
    - "Một cán bộ trại giam": Đây là cụm danh từ chỉ người (nghề nghiệp/vị trí), nhưng không phải là đối tượng chính được nhắc đến trong sự kiện cụ thể này.
    - "Nghĩa": Đây là tên riêng của một cá nhân, đóng vai trò là chủ thể được nhắc đến trong câu. Do đó, "Nghĩa" được xác định là thực thể loại `Person`.

- Bước 2: Phân tích các sự kiện và trigger.
    - Trong câu có cụm từ "bị biệt giam trong tù". Từ "giam" (nằm trong cụm "biệt giam") là hành động tước tự do, giữ người lại trong cơ sở giam giữ. Đây là hành vi liên quan đến việc quản lý phạm nhân/người bị tạm giam, thuộc loại sự kiện `Justice:Arrest-Jail`.

- Bước 3: Xác định các đối số cho sự kiện.
    - Với trigger "giam" (hành động giam giữ), đối tượng chịu tác động trực tiếp của việc bị giam là "Nghĩa". Do đó, "Nghĩa" được gán vào vai trò `Person` (người bị giam) trong sự kiện này.

- Bước 4: Kết luận và tổng hợp kết quả.
    - Thực thể: "Nghĩa" (Person).
    - Sự kiện: `Justice:Arrest-Jail` với trigger "giam" và đối số là "Nghĩa".

{
  "entities": [
    {"text": "Nghĩa", "type": "Person"}
  ],
  "events": [
    {
      "type": "Justice:Arrest-Jail",
      "trigger": "giam",
      "arguments": [
        {"text": "Nghĩa", "type": "Person"}
      ]
    }
  ]
}

--- Ví dụ 3 ---
Câu: "Bộ Quốc phòng Nga hôm nay ra thông cáo khẳng định Israel đứng sau vụ tấn công bằng tên lửa hành trình nhằm vào sân bay T -4 , cơ sở quân sự quan trọng của Syria ở phía đông tỉnh Homs , Interfax đưa tin ."

- Bước 1: Phân tích các thực thể trong câu.
    - "Bộ Quốc phòng Nga": Đây là tên một cơ quan nhà nước, thuộc về chính phủ Nga, nên được phân loại là `Organization`.
    - Các thực thể khác như "Israel", "Syria", "Homs" (địa danh), "sân bay T -4" (cơ sở hạ tầng) cũng xuất hiện nhưng không nằm trong danh sách mục tiêu cần trích xuất.

- Bước 2: Xác định các sự kiện và trigger.
    - Cụm từ "ra thông cáo khẳng định" đóng vai trò là hành động đưa ra một tuyên bố chính thức, mang tính chất cáo buộc hoặc khẳng định về một sự việc. Trong ngữ cảnh này, "thông cáo" được xác định là trigger cho sự kiện `Justice:Charge-Indict` (khởi tố/buộc tội), vì thông cáo này chứa đựng nội dung buộc tội Israel đứng sau một vụ tấn công.

- Bước 3: Xác định các đối số cho sự kiện.
    - Với trigger "thông cáo", chủ thể thực hiện hành động đưa ra thông cáo/cáo buộc này là "Bộ Quốc phòng Nga". Do đó, "Bộ Quốc phòng Nga" được gán vai trò là `Prosecutor` (người/cơ quan đưa ra cáo buộc).

- Bước 4: Tổng hợp kết quả.
    - Thực thể: "Bộ Quốc phòng Nga" (Organization).
    - Sự kiện: `Justice:Charge-Indict` với trigger "thông cáo" và đối số là "Bộ Quốc phòng Nga" (Prosecutor).

{
  "entities": [
    {"text": "Bộ Quốc phòng Nga", "type": "Organization"}
  ],
  "events": [
    {
      "type": "Justice:Charge-Indict",
      "trigger": "thông cáo",
      "arguments": [
        {"text": "Bộ Quốc phòng Nga", "type": "Prosecutor"}
      ]
    }
  ]
}

--- Ví dụ 4 ---
Câu: "Những người này thông báo cho Khodorkovsky rằng người mẹ bị ung thư của ông đang ngày càng yếu đi và cảnh báo về khả năng diễn ra phiên xét xử ông lần thứ ba ."

- Bước 1: Phân tích các thực thể trong câu.
    - "Khodorkovsky": Là tên riêng của một cá nhân, thuộc loại Person.
    - "người mẹ": Chỉ người thân trong gia đình, là một cụm danh từ chỉ người.
    - "ông": Trong ngữ cảnh này, "ông" là đại từ nhân xưng dùng để chỉ Khodorkovsky (người đang được nhắc đến), thuộc loại Person.
    - "người này": Chỉ một nhóm người tham gia vào hành động thông báo.

- Bước 2: Phân tích các sự kiện trong câu.
    - Cụm từ "phiên xét xử" liên quan đến một thủ tục pháp lý tại tòa án. Đây là sự kiện về việc tổ chức một phiên tòa để xem xét tội danh, do đó nó thuộc loại Justice:Trial-Hearing. Trigger chính là "xét xử".

- Bước 3: Xác định các đối số cho sự kiện.
    - Với sự kiện "xét xử" (Justice:Trial-Hearing), đối tượng là người sẽ phải tham gia phiên tòa, chịu sự xem xét của pháp luật chính là "ông" (tức Khodorkovsky). Do đó, "ông" đóng vai trò là Defendant (bị cáo/người bị xét xử).

- Bước 4: Kết luận và tổng hợp kết quả.
    - Thực thể cần trích xuất là "ông" (Person).
    - Sự kiện là "xét xử" (Justice:Trial-Hearing) với đối số là "ông" (Defendant).

{
  "entities": [
    {"text": "ông", "type": "Person"}
  ],
  "events": [
    {
      "type": "Justice:Trial-Hearing",
      "trigger": "xét xử",
      "arguments": [
        {"text": "ông", "type": "Defendant"}
      ]
    }
  ]
}

--- Ví dụ 5 ---
Câu: "Người dân kiểm tra một khu vực bị đòn tấn công ở khu gần thủ đô Damascus và miền nam Syria đang bị phe đối lập kiểm soát , thành phố Aleppo , ngày 26/7 ."

- Bước 1: Phân tích các thực thể trong câu.
    - Cụm từ "gần thủ đô Damascus và miền nam Syria" chỉ một khu vực địa lý cụ thể bao gồm các thành phố và vùng lãnh thổ, do đó được phân loại là `Location`.
    - Các thực thể khác như "Người dân", "phe đối lập", "thành phố Aleppo" và mốc thời gian "ngày 26/7" cũng xuất hiện nhưng không nằm trong danh sách mục tiêu cần trích xuất.

- Bước 2: Xác định các sự kiện.
    - Cụm từ "đòn tấn công" chỉ một hành vi bạo lực, tấn công vũ trang hoặc xung đột đang diễn ra. Điều này khớp với loại sự kiện `Conflict:Attack`.

- Bước 3: Xác định các đối số cho sự kiện.
    - Với trigger "đòn tấn công", ta cần xác định nơi diễn ra hành vi này. Cụm từ "gần thủ đô Damascus và miền nam Syria" là địa điểm nơi cuộc tấn công xảy ra, vì vậy nó được gán cho tham số `Place`.

- Bước 4: Tổng hợp kết quả.
    - Kết quả trích xuất bao gồm thực thể `Location` và sự kiện `Conflict:Attack` với đối số `Place` tương ứng.

{
  "entities": [
    {"text": "gần thủ đô Damascus và miền nam Syria", "type": "Location"}
  ],
  "events": [
    {
      "type": "Conflict:Attack",
      "trigger": "đòn tấn công",
      "arguments": [
        {"text": "gần thủ đô Damascus và miền nam Syria", "type": "Place"}
      ]
    }
  ]
}
"""
